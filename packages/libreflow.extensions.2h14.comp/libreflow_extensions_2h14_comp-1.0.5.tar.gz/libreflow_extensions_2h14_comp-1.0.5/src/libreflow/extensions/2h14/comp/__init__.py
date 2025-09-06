import os
import mimetypes
import re
import subprocess
import time
import platform

from pprint import pprint
from kabaret import flow
from kabaret.app import resources
from kabaret.flow_contextual_dict import get_contextual_dict
from libreflow.resources import file_templates
from libreflow.utils.b3d import wrap_python_expr
from libreflow.baseflow.film import Film
from libreflow.baseflow.task import Task
from libreflow.baseflow.site import SiteJobsPoolNames
from libreflow.baseflow.runners import FILE_EXTENSION_ICONS

from libreflow.baseflow.file import (
    GenericRunAction,
    LinkedJob,
    FileJob,
    RenderAEPlayblast,
    SelectAEPlayblastRenderMode,
    TrackedFile,
    TrackedFolder,
    MarkImageSequence,
    WaitProcess,
    FileRevisionNameChoiceValue,
    AERenderSettings,
    AEOutputModule
)
from libreflow.extensions.runner.tvpaint_playblast import ExportTVPaintLayersJob

from . import scripts


#
#       PLAYBLAST
#


class RenderQualityChoiceValue(flow.values.ChoiceValue):
    CHOICES = ["Preview (H.264)", "Final (ProRes)"]


class SelectAEPlayblastComp(SelectAEPlayblastRenderMode):
    # Action startup with parameter selection

    ICON = ("icons.libreflow", "afterfx")

    render_quality = flow.Param("Preview (H.264)", RenderQualityChoiceValue)

    with flow.group('Advanced settings'):
        render_settings = flow.SessionParam(None, AERenderSettings)
        output_module = flow.SessionParam(None, AEOutputModule)
        start_frame = flow.IntParam()
        end_frame = flow.IntParam()

    def get_buttons(self):
        return ["Render", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        # Get AfterEffects templates configured in current site
        site = self.root().project().get_current_site()
        render_settings = (site.ae_render_settings_templates.get() or {}).get(
            self.render_settings.get()
        )
        output_module = (site.ae_output_module_templates.get() or {}).get(
            self.output_module.get()
        )
        audio_output_module = site.ae_output_module_audio.get()

        if button == "Render":
            render_action = self._file.render_ae_playblast
            render_action.render_quality.set(self.render_quality.get())
            render_action.revision.set(self.revision.get())
            render_action.render_settings.set(render_settings)
            render_action.output_module.set(output_module)
            render_action.audio_output_module.set(audio_output_module)
            render_action.start_frame.set(self.start_frame.get())
            render_action.end_frame.set(self.end_frame.get())

            if (
                self.start_frame.get() is not None or self.end_frame.get() is not None
            ) and self._has_render_folder():
                return self.get_result(
                    next_action=self._file.select_ae_playblast_render_mode_page2.oid()
                )

            render_action.run("Render")


class RenderAEPlayblastComp(RenderAEPlayblast):
    # Render img sequence in after fx

    render_quality = flow.Param()

    def _render_wait(self, folder_name, revision_name, render_pid, export_audio_pid):
        render_wait = self._file.final_render_wait
        render_wait.folder_name.set(folder_name)
        render_wait.revision_name.set(revision_name)
        render_wait.wait_pid(render_pid)
        render_wait.wait_pid(export_audio_pid)
        render_wait.run(None)

    def run(self, button):
        if button == "Cancel":
            return

        revision_name = self.revision.get()

        # Render image sequence
        ret = self._render_image_sequence(
            revision_name,
            self.render_settings.get(),
            self.output_module.get(),
            self.start_frame.get(),
            self.end_frame.get(),
        )
        render_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(ret["runner_id"])
        )
        # Export audio
        ret = self._export_audio(revision_name, self.audio_output_module.get())
        export_audio_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(ret["runner_id"])
        )

        folder_name = self._file.name()[: -len(self._file.format.get())]
        folder_name += "render"

        if self.render_quality.get() == "Preview (H.264)":
            # Configure and start image sequence marking for preview output
            self._mark_image_sequence(
                folder_name,
                revision_name,
                render_pid=render_runner["pid"],
                export_audio_pid=export_audio_runner["pid"],
            )

        if self.render_quality.get() == "Final (ProRes)":
            # Configure and start image sequence conversion for final output
            self._render_wait(
                folder_name,
                revision_name,
                render_pid=render_runner["pid"],
                export_audio_pid=export_audio_runner["pid"],
            )


class WaitFinalRender(WaitProcess):
    # Image sequence conversion for Final output

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)

    folder_name = flow.Param()
    revision_name = flow.Param()

    def get_run_label(self):
        return "Convert image sequence"

    def _ensure_file_revision(self, name, revision_name):
        mng = self.root().project().get_task_manager()
        default_files = mng.get_task_files(self._task.name())

        # Find matching default file
        match_dft_file = False
        for file_mapped_name, file_data in default_files.items():
            # Get only files
            if "." in file_data[0]:
                base_name, extension = os.path.splitext(file_data[0])
                if name == base_name:
                    extension = extension[1:]
                    path_format = file_data[1]
                    match_dft_file = True
                    break

        # Fallback to default mov container
        if match_dft_file is False:
            extension = "mov"
            path_format = mng.get_task_path_format(
                self._task.name()
            )  # get from default task

        mapped_name = name + "_" + extension

        if not self._files.has_mapped_name(mapped_name):
            file = self._files.add_file(
                name, extension, tracked=True, default_path_format=path_format
            )
        else:
            file = self._files[mapped_name]

        if not file.has_revision(revision_name):
            revision = file.add_revision(revision_name)
            file.set_current_user_on_revision(revision_name)
        else:
            revision = file.get_revision(revision_name)

        file.file_type.set("Outputs")
        file.ensure_last_revision_oid()

        return revision

    def _get_first_image_path(self, revision):
        img_folder_path = revision.get_path()

        for f in os.listdir(img_folder_path):
            file_path = os.path.join(img_folder_path, f)
            file_type = mimetypes.guess_type(file_path)[0].split("/")[0]

            if file_type == "image":
                return file_path

        return None

    def _get_audio_path(self, folder_name):
        if any("_aep" in file for file in self._files.mapped_names()):
            scene_name = folder_name.replace("_render", "_aep")
        else:
            scene_name = re.search(r"(.+?(?=_render))", folder_name).group()

        if not self._files.has_mapped_name(scene_name):
            # Scene not found
            return None

        return self._files[scene_name].export_ae_audio.get_audio_path()

    def launcher_exec_func_kwargs(self):
        return dict(
            folder_name=self.folder_name.get(), revision_name=self.revision_name.get()
        )

    def _do_after_process_ends(self, *args, **kwargs):
        self.root().project().ensure_runners_loaded()
        sequence_folder = self._files[kwargs["folder_name"]]

        rev = sequence_folder.get_revision(kwargs["revision_name"])
        path = self._get_first_image_path(rev)
        input_path = path.replace("0000.png", r"%04d.png")

        print("INPUT_PATH = " + input_path)

        output_name = kwargs["folder_name"].replace("_render", "_movie")
        output_rev = self._ensure_file_revision(output_name, kwargs["revision_name"])
        output_path = output_rev.get_path()

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        print("OUTPUT PATH = " + output_path)

        audio_path = self._get_audio_path(kwargs["folder_name"])

        print("AUDIO PATH = " + audio_path)

        process = subprocess.run(
            f"ffmpeg -y -r 25 -i {input_path} -i {audio_path} -c:a aac -map 0:0 -map 1:0 -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 -pix_fmt yuv422p10le {output_path}",
            check=False,
            shell=True,
        )

        print(f"COMMAND:\n{' '.join(process.args)}")
        print(f"STDERR: {repr(process.stderr)}")
        print(f"STDOUT: {process.stdout}")
        print(f"RETURN CODE: {process.returncode}")

        if not os.path.exists(output_path):
            self.message.set(
                (
                    "<h2>Upload playblast to Kitsu</h2>"
                    "<font color=#FF584D>File conversion failed</font>"
                )
            )
            return self.get_result(close=False)


class MarkSequencePreview(MarkImageSequence):
    # Image sequence marking and conversion for preview output

    def mark_sequence(self, revision_name):
        # Compute playblast prefix
        prefix = self._folder.name()
        prefix = prefix.replace("_render", "")

        source_revision = self._file.get_revision(revision_name)
        revision = self._ensure_file_revision(prefix + "_preview_movie", revision_name)
        revision.comment.set(source_revision.comment.get())

        # Get the path of the first image in folder
        img_path = self._get_first_image_path(revision_name)

        # Get original file name to print on frames
        if self._files.has_mapped_name(prefix + "_aep"):
            scene = self._files[prefix + "_aep"]
            file_name = scene.complete_name.get() + "." + scene.format.get()
        else:
            file_name = self._folder.complete_name.get()

        self._extra_argv = {
            "image_path": img_path,
            "video_output": revision.get_path(),
            "file_name": file_name,
            "audio_file": self._get_audio_path(),
        }

        return super(MarkImageSequence, self).run("Render")


#
#       SCENE BUILDER
#

class KitsuStatusEndProcess(WaitProcess):

    _task = flow.Parent()
    _shot = flow.Parent(3)
    _sequence = flow.Parent(5)

    def allow_context(self, context):
        return False

    def _do_after_process_ends(self, *args, **kwargs):
        """
        Subclasses may redefine this method to perform a particular
        processing after the subprocess ending.
        """
        # Trigger kitsu login
        kitsu_url = self.root().project().admin.kitsu.server_url.get()
        self.root().project().kitsu_api().set_host(f"{kitsu_url}/api")
        kitsu_status = self.root().project().show_login_page()
        if kitsu_status:
            raise Exception(
                "No connection with Kitsu host. Log in to your account in the GUI session."
            )
            return

        kitsu = self.root().project().kitsu_api()
        comment = f"le job est terminé"
        kitsu.set_shot_task_status(
            self._sequence.name(),
            self._shot.name(),
            "Rendering" if self._task.name() == "color" else self._task.name(),
            "Done" if self._task.name() == "color" else "GO_ON",
            comment,
        )


class ChangeKitsuStatus(flow.Action):
    _is_job = flow.Param()
    _pool_name = flow.Param()
    _status = flow.Param()
    _job_type = flow.Param()

    _task = flow.Parent()
    _shot = flow.Parent(3)
    _sequence = flow.Parent(5)

    def allow_context(self, context):
        return context

    def run(self, button):
        site = self.root().project().get_current_site().name()
        kitsu = self.root().project().kitsu_api()

        if self._is_job.get() is False:
            self._pool_name.set(platform.node())
            comment = f"un job {self._job_type.get()} a démarré sur le site {site}, avec la machine {self._pool_name.get()}"
        else:
            comment = f"un job {self._job_type.get()} a été envoyé sur le site {site}, sur le pool {self._pool_name.get()}"

        kitsu.set_shot_task_status(
            self._sequence.name(),
            self._shot.name(),
            "Rendering" if self._task.name() == "color" else self._task.name(),
            self._status.get(),
            comment,
        )


class InitCompSceneJob(FileJob):
    _task = flow.Parent(2)

    def get_label(self):
        return "INIT COMP SCENE JOB"

    def _do_job(self):
        session = self.root().session()

        session.log_info(f"[{self.get_label()}] Start - {self.get_time()}")

        self.root().project().ensure_runners_loaded()

        # Trigger kitsu login
        kitsu_url = self.root().project().admin.kitsu.server_url.get()
        self.root().project().kitsu_api().set_host(f"{kitsu_url}/api")
        kitsu_status = self.root().project().show_login_page()
        if kitsu_status:
            raise Exception(
                "No connection with Kitsu host. Log in to your account in the GUI session."
            )
            return

        init_comp = self._task.init_comp_scene
        init_comp.dependencies.touch()

        if init_comp.missing_deps:
            self.root().session().log_error(
                f"[JOB INFO]\n{init_comp.dependencies._dependencies_data}"
            )
            raise Exception("Some dependencies are missing")
            return

        ae_runner, kitsu_runner = init_comp.run("Build")
        self.wait_runner([ae_runner["runner_id"], kitsu_runner["runner_id"]])

        session.log_info(f"[{self.get_label()}] End - {self.get_time()}")


class SubmitInitCompSceneJob(flow.Action):
    _task = flow.Parent()

    pool = flow.Param("default", SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor="int")

    revision = flow.Param().ui(hidden=True)

    def get_buttons(self):
        self.message.set("<h2>Submit init comp scene to pool</h2>")
        self.pool.apply_preset()
        return ["Submit", "Cancel"]

    def allow_context(self, context):
        return False

    def _get_job_label(self):
        settings = get_contextual_dict(self._task, "settings")
        task_label = [
            settings["project_name"],
            settings["sequence"],
            settings["shot"],
            settings["task"],
        ]
        label = f"Init Comp Scene - {' '.join(task_label)}"
        return label

    def run(self, button):
        if button == "Cancel":
            return

        # Update pool preset
        self.pool.update_preset()

        job = self._task.jobs.create_job(job_type=InitCompSceneJob)
        site_name = self.root().project().get_current_site().name()

        self._task.change_kitsu_status._is_job.set(True)
        self._task.change_kitsu_status._job_type.set("de build")
        self._task.change_kitsu_status._status.set("ON_HOLD")
        self._task.change_kitsu_status._pool_name.set(self.pool.get())
        self._task.change_kitsu_status.run("run")

        job.submit(
            pool=site_name + "_" + self.pool.get(),
            priority=self.priority.get(),
            label=self._get_job_label(),
            creator=self.root().project().get_user_name(),
            owner=self.root().project().get_user_name(),
            paused=False,
            show_console=False,
        )


class CompDependency(flow.Object):
    task_name = flow.Computed()
    file_name = flow.Computed()
    revision = flow.Computed()
    path = flow.Computed()

    _map = flow.Parent()

    def extension(self):
        ext = os.path.splitext(self.file_name.get())[1]
        if ext:
            ext = ext[1:]
        return ext

    def compute_child_value(self, child_value):
        if child_value is self.task_name:
            self.task_name.set(self._map.get_task_name(self.name()))
        elif child_value is self.file_name:
            self.file_name.set(self._map.get_file_name(self.name()))
        elif child_value is self.revision:
            self.revision.set(self._map.get_revision(self.name()))
        elif child_value is self.path:
            self.path.set(self._map.get_path(self.name()))


class RefreshDependencies(flow.Action):
    ICON = ("icons.libreflow", "refresh")

    _map = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._map.touch()


class CompDependencies(flow.DynamicMap):
    ICON = ("icons.libreflow", "dependencies")
    STYLE_BY_STATUS = {"available": ("icons.gui", "available")}

    refresh = flow.Child(RefreshDependencies)

    _action = flow.Parent()
    _shot = flow.Parent(4)
    _sequence = flow.Parent(6)

    @classmethod
    def mapped_type(cls):
        return CompDependency

    def __init__(self, parent, name):
        super(CompDependencies, self).__init__(parent, name)
        self._dependencies_data = None

    def mapped_names(self, page_num=0, page_size=None):
        if self._dependencies_data is None:
            self._dependencies_data = {}

            kitsu_api = self.root().project().kitsu_api()
            shot_data = kitsu_api.get_shot_data(
                self._shot.name(), self._sequence.name()
            )

            for task_name, file_name, revision, optional in self._get_dependencies():
                if revision is None and optional:
                    # Specific use case for not tracking shots
                    if shot_data:
                        if (
                            shot_data["data"]["cam"] != "TRACKING"
                            and file_name == "tracking_camera.jsx"
                        ) or (
                            shot_data["data"]["shot_type"] == "NO ANIM"
                            and file_name == "layers"
                        ):
                            continue

                mapped_name = "%s_%s" % (task_name, file_name.replace(".", "_"))
                self._dependencies_data[mapped_name] = {
                    "task_name": task_name,
                    "file_name": file_name,
                    "path": revision.get_path() if revision else None,
                    "revision": revision.name() if revision else None,
                }

        self._action.get_buttons()

        return self._dependencies_data.keys()

    def columns(self):
        return ["Status", "Dependency", "Revision"]

    def get_dependency(self, department, file_name):
        mapped_name = "%s_%s" % (department, file_name.replace(".", "_"))
        try:
            return self.get_mapped(mapped_name)
        except flow.exceptions.MappedNameError:
            return None

    def get_task_name(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data[mapped_name]["task_name"]

    def get_file_name(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data[mapped_name]["file_name"]

    def get_revision(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data[mapped_name]["revision"]

    def get_path(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data[mapped_name]["path"]

    def touch(self):
        self._dependencies_data = None
        super(CompDependencies, self).touch()

    def _get_dependencies(self):
        deps = [
            (("animatic", "animatic_edit.mov"), False),
            (("tracking", "tracking_camera.jsx"), True),
            (("background", "background.psd"), False),
            (("compositing", "layers"), True),
        ]
        return [self._get_dependency_data(d) for d in deps]

    def _get_dependency_data(self, dependency):
        revision = None
        target, optional = dependency
        task_name = file_name = None

        if type(target) is tuple:
            task_name, file_name = target
            revision = self._get_target_revision(task_name, file_name)
        elif type(target) is list:
            # Get the first existing dependency
            for t, f in target:
                task_name, file_name = t, f
                revision = self._get_target_revision(task_name, file_name)
                if revision is not None:
                    break

        return task_name, file_name, revision, optional

    def _get_target_revision(self, task_name, file_name):
        file_name = file_name.replace(".", "_")
        oid = f"{self._shot.oid()}/tasks/{task_name}/files/{file_name}"
        r = None

        try:
            f = self.root().get_object(oid)
        except (ValueError, flow.exceptions.MappedNameError):
            pass
        else:
            r = f.get_head_revision()
            if r is not None and not r.exists():
                r = None

        return r

    def _fill_row_cells(self, row, item):
        row["Status"] = ""
        row["Dependency"] = "%s/%s" % (
            item.task_name.get() or "undefined",
            item.file_name.get() or "undefined",
        )
        row["Revision"] = item.revision.get()

    def _fill_row_style(self, style, item, row):
        style["Status_icon"] = (
            "icons.libreflow",
            "warning" if item.path.get() is None else "available",
        )

        style["Dependency_icon"] = FILE_EXTENSION_ICONS.get(
            item.extension(), ("icons.gui", "folder-white-shape")
        )


class InitCompScene(GenericRunAction):
    ICON = ("icons.libreflow", "afterfx")

    dependencies = flow.Child(CompDependencies).ui(expanded=True)

    _task = flow.Parent()
    _shot = flow.Parent(3)
    _sequence = flow.Parent(5)

    def __init__(self, parent, name):
        super(InitCompScene, self).__init__(parent, name)
        self._comp_scene_path = None
        self.missing_deps = False
        self.missing_template = False

    def allow_context(self, context):
        return context

    def runner_name_and_tags(self):
        return "AfterEffects", []

    def get_run_label(self):
        return "Build compositing scene"

    def target_file_extension(self):
        return "aep"

    def needs_dialog(self):
        return True

    def get_buttons(self):
        msg = "<h2>Build compositing shot</h2>"
        if any(
            data["path"] is None
            for data in self.dependencies._dependencies_data.values()
        ):
            self.missing_deps = True
            msg += "\n<font color=#FFA34D>Some dependencies are not available on your site.</font>\n"
        else:
            self.missing_deps = False
        
        if self.missing_template:
            msg += "\n<font color=#FFA34D>Template file are not available on your site.</font><br><br>Please download the latest revision on<br>/_2h14/films/_2h14_test/sequences/sq999/shots/sh9999/tasks/compositing/"
            self.missing_template = False

        self.message.set(msg)

        buttons = ["Build", "Cancel"]
        if (
            self.root().project().get_current_site().site_type.get() == "Studio"
            and self.root().project().get_current_site().pool_names.get()
        ):
            buttons.insert(1, "Submit job")
        return buttons

    def extra_argv(self):
        kitsu_api = self.root().project().kitsu_api()

        script_path = resources.get("scripts", "init_comp_scene.jsx").replace("\\", "/")
        width = 3840
        height = 1634
        fps = 25
        duration = kitsu_api.get_shot_duration(self._shot.name(), self._sequence.name())

        base_comp_name = f"{self._sequence.name()}_{self._shot.name()}"

        script_str = f"//@include '{script_path}'\n"

        script_str += f"openScene('{self._comp_scene_path}');\n"

        # Include tracking script if needed
        tracking_path = self.get_dependency_path("tracking", "tracking_camera.jsx")
        if tracking_path is not None:
            script_str += f"//@include '{tracking_path}'\n"

        script_str += f"setupScene('{base_comp_name}', {width}, {height}, {fps}, {duration});\n"

        # Import Background
        background_path = self.get_dependency_path("background", "background.psd")
        if background_path is not None:
            script_str += f"importPSDBackground('{background_path}', {fps}, {duration}, '{base_comp_name}');\n"

        # Import Animatic
        animatic_path = self.get_dependency_path("animatic", "animatic_edit.mov")
        if animatic_path is not None:
            script_str += f"importAnimatic('{animatic_path}', '{base_comp_name}');\n"

        # Import TVPaint layers
        layers_path = self.get_dependency_path("compositing", "layers")
        json_name = f"{self._sequence.name()}_{self._shot.name()}_layers_data.json"
        if layers_path is not None:
            script_str += f"importAnimationLayers('{layers_path}', '{json_name}', '{base_comp_name}');\n"

        # Save After Effects file
        script_str += f"saveScene('{self._comp_scene_path}', '{base_comp_name}');\n"

        # args = ["-m", "-s", script_str]
        args = ['-m', '-s', script_str, '-noui']
        return args

    def get_dependency_path(self, task_name, file_name):
        path = None
        d = self.dependencies.get_dependency(task_name, file_name)
        if d is not None:
            path = d.path.get().replace("\\", "/")

        return path

    def get_default_file(self, task_name, file_mapped_name):
        mng = self.root().project().get_task_manager()
        if not mng.default_tasks.has_mapped_name(task_name):  # check default task
            # print(f'Scene Builder - no default task {task_name} -> use default template')
            return None

        dft_task = mng.default_tasks[task_name]
        if not dft_task.files.has_mapped_name(file_mapped_name):  # check default file
            # print(f'Scene Builder - default task {task_name} has no default file {filename} -> use default template')
            return None

        return dft_task.files[file_mapped_name]

    def get_template_file(self, dft_file):
        template_file = self.root().get_object(dft_file.template_file.get())

        if template_file is not None:
            template_file_revision = dft_file.template_file_revision.get()
            if template_file_revision == 'Latest':
                source_revision = template_file.get_head_revision(sync_status='Available')
            else:
                source_revision = template_file.get_revision(template_file_revision)

        if source_revision is not None and os.path.exists(source_revision.get_path()):
            return source_revision.get_path()

        return None

    def ensure_comp_scene(self):
        files = self._task.files
        name = "compositing"
        ext = "aep"
        file_name = "%s_%s" % (name, ext)
        dft_file = self.get_default_file(self._task.name(), file_name)
        path_format = dft_file.path_format.get()
        template_path = self.get_template_file(dft_file)
        if template_path is None:
            self.missing_template = True
            self.get_buttons()
            return None

        if files.has_file(name, ext):
            _file = files[file_name]
        else:
            _file = files.add_file(
                name=name,
                extension=ext,
                tracked=True,
                default_path_format=path_format,
            )
        _file.create_working_copy(source_path=template_path)
        _file.check_scene_dependencies.dependencies._dependencies_data.set(
            self.dependencies._dependencies_data
        )
        rev = _file.publish(comment="Created with comp scene builder")
        return rev.get_path()

    def run(self, button):
        if button == "Cancel":
            return
        elif self.missing_deps:
            return self.get_result(close=False)
        elif button == "Submit job":
            submit_action = self._task.submit_init_comp_scene_job
            return self.get_result(next_action=submit_action.oid())
        
        self._task.change_kitsu_status._is_job.set(False)
        self._task.change_kitsu_status._job_type.set("de build")
        self._task.change_kitsu_status._status.set("Work In Progress")

        self._task.change_kitsu_status.run("run")

        self._comp_scene_path = self.ensure_comp_scene().replace("\\", "/")
        if self._comp_scene_path is None:
            return self.get_result(close=False)
        runner_dict = super(InitCompScene, self).run(button)
        ae_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(runner_dict["runner_id"])
        )

        self._task.kitsu_status_end_process.wait_pid(ae_runner["pid"])
        wait_dict = self._task.kitsu_status_end_process.run('wait')
        return runner_dict, wait_dict
    


class CompDependenciesStatus(CompDependencies):
    STYLE_BY_STATUS = {"up_to_date": ("icons.gui", "available")}

    _action = flow.Parent()
    _task = flow.Parent(4)
    _shot = flow.Parent(6)
    _sequence = flow.Parent(8)

    _dependencies_data = flow.Param().ui(hidden=True)

    def __init__(self, parent, name):
        super(CompDependencies, self).__init__(parent, name)

    def mapped_names(self, page_num=0, page_size=None):
        return self._dependencies_data.get().keys()

    def get_task_name(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data.get()[mapped_name]["task_name"]

    def get_file_name(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data.get()[mapped_name]["file_name"]

    def get_revision(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data.get()[mapped_name]["revision"]

    def get_path(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data.get()[mapped_name]["path"]

    def columns(self):
        return ["Status", "Dependency", "Imported Revision", "Last Revision"]

    def _get_target_revision(self, task_name, file_name):
        file_name = file_name.replace(".", "_")
        oid = f"{self._shot.oid()}/tasks/{task_name}/files/{file_name}"
        r = None

        try:
            f = self.root().get_object(oid)
        except (ValueError, flow.exceptions.MappedNameError):
            pass
        else:
            r = f.get_head_revision()

        return r

    def _fill_row_cells(self, row, item):
        row["Status"] = ""
        row["Dependency"] = "%s/%s" % (
            item.task_name.get() or "undefined",
            item.file_name.get() or "undefined",
        )
        row["Imported Revision"] = item.revision.get()
        row["Last Revision"] = self._get_target_revision(item.task_name.get(), item.file_name.get()).name()

    def _fill_row_style(self, style, item, row):
        last_rev = self._get_target_revision(item.task_name.get(), item.file_name.get())

        rev_val = int(item.revision.get().replace("v", ""))
        last_rev_val = int(last_rev.name().replace("v", ""))

        style["Status_icon"] = (
            "icons.libreflow",
            "warning" if last_rev_val > rev_val else "available",
        )

        if not last_rev.exists():
            style["Last Revision_foreground_color"] = "#606060"


class CompDependenciesCheck(GenericRunAction):
    ICON = ("icons.libreflow", "afterfx")

    dependencies = flow.Child(CompDependenciesStatus).ui(expanded=True)

    _shot = flow.Parent(5)
    _sequence = flow.Parent(7)

    def __init__(self, parent, name):
        super(CompDependenciesCheck, self).__init__(parent, name)
        self._comp_scene_path = None
        self.to_update = []

    def allow_context(self, context):
        return (
            context and len(self._file.get_revision_names(sync_status="Available")) > 0
        )

    def runner_name_and_tags(self):
        return "AfterEffects", []

    def get_run_label(self):
        return "Update compositing scene"

    def target_file_extension(self):
        return "aep"

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.to_update = []
        self.message.set("")

        for item in self.dependencies.mapped_items():
            status = self._get_map_data(item, "_style")["Status_icon"][1]
            if status != "available":
                if self._get_target_revision(
                    item.task_name.get(), item.file_name.get()
                ):
                    self.to_update.append(item.file_name.get())
                else:
                    self.message.set(
                        """<font color = orange>
                    At least one revision is missing locally and needs to be downloaded before updating
                    </font>"""
                    )

        if self.to_update:
            return ["Update", "Cancel"]

        return ["Cancel"]

    def _get_map_data(self, item, col):
        return self.dependencies.row(item)[1][col]

    def _get_target_revision(self, task_name, file_name):
        file_name = file_name.replace(".", "_")
        oid = f"{self._shot.oid()}/tasks/{task_name}/files/{file_name}"
        r = None

        try:
            f = self.root().get_object(oid)
        except (ValueError, flow.exceptions.MappedNameError):
            pass
        else:
            r = f.get_head_revision()
            if r is not None and not r.exists():
                r = None

        return r

    def get_dependency_revision(self, task_name, file_name):
        d = self.dependencies.get_dependency(task_name, file_name)
        if d is not None:
            r = self._get_target_revision(task_name, file_name)

        return r

    def extra_argv(self):
        deps_data = self.dependencies._dependencies_data.get()

        kitsu_api = self.root().project().kitsu_api()

        script_path = resources.get("scripts", "init_comp_scene.jsx").replace("\\", "/")
        fps = 25
        duration = kitsu_api.get_shot_duration(self._shot.name(), self._sequence.name())

        base_comp_name = f"{self._sequence.name()}_{self._shot.name()}"

        script_str = f"//@include '{script_path}'\n"

        script_str += f"openScene('{self._comp_scene_path}');\n"

        # Update Background
        if "background.psd" in self.to_update:
            self.root().session().log_info("Updating background dependency")
            background_rev = self.get_dependency_revision(
                "background", "background.psd"
            )
            background_path = background_rev.get_path().replace("\\", "/")
            if background_path is not None:
                script_str += f"updatePSDBackground('{background_path}', {fps}, {duration}, '{base_comp_name}');\n"
                deps_data["background_background_psd"]["revision"] = (
                    background_rev.name()
                )
                deps_data["background_background_psd"]["path"] = (
                    background_rev.get_path()
                )

        # Update Animatic
        if "animatic_edit.mov" in self.to_update:
            self.root().session().log_info("Updating animatic dependency")
            animatic_rev = self.get_dependency_revision("animatic", "animatic_edit.mov")
            animatic_path = animatic_rev.get_path().replace("\\", "/")
            if animatic_path is not None:
                script_str += (
                    f"importAnimatic('{animatic_path}', '{base_comp_name}');\n"
                )
                deps_data["animatic_animatic_edit_mov"]["revision"] = (
                    animatic_rev.name()
                )
                deps_data["animatic_animatic_edit_mov"]["path"] = (
                    animatic_rev.get_path()
                )

        # Update TVPaint layers
        if "layers" in self.to_update:
            self.root().session().log_info("Updating animation layers dependency")
            layers_rev = self.get_dependency_revision("compositing", "layers")
            layers_path = layers_rev.get_path().replace("\\", "/")
            json_name = f"{self._sequence.name()}_{self._shot.name()}_layers_data.json"
            if layers_path is not None:
                script_str += f"updateAnimationLayers('{layers_path}', '{json_name}', '{base_comp_name}');\n"
                deps_data["compositing_layers"]["revision"] = layers_rev.name()
                deps_data["compositing_layers"]["path"] = layers_rev.get_path()

        # Save After Effects file
        script_str += f"saveScene('{self._comp_scene_path}', '{base_comp_name}');\n"

        args = ["-m", "-s", script_str, "-noui"]
        # args = ["-m", "-s", script_str]

        self.dependencies._dependencies_data.set(deps_data)

        return args

    def run(self, button):
        if button == "Cancel":
            return

        head_rev = self._file.get_head_revision()

        self._file.create_working_copy(from_revision=head_rev.name())

        self._file.publish_action.comment.set(
            f"Updated dependencies : {self.to_update}"
        )
        self._file.publish_action.keep_editing.set(False)
        self._file.publish_action.run("Publish")

        self._comp_scene_path = (
            self._file.get_head_revision().get_path().replace("\\", "/")
        )

        return super(CompDependenciesCheck, self).run(button)


class CleanTrackingJSX(WaitProcess):
    jsx_path = flow.Param()

    def allow_context(self, context):
        return False

    def get_run_label(self):
        return "Clean tracking_camera.jsx"

    def _do_after_process_ends(self, *args, **kwargs):
        if os.path.isfile(self.jsx_path.get()):
            with open(self.jsx_path.get(), "r") as jsxf:
                content = jsxf.read()

                # Forego prompt for comp name
                sub_pattern = r"""var compName = prompt\("[^"]*","(.*)","[^"]*"\);"""
                content = re.sub(sub_pattern, r'var compName = "\1";\n', content)

            with open(self.jsx_path.get(), "w") as jsxf:
                jsxf.write(content)

        self.root().session().log_info(
            "[CLEAN TRACKING JSX] Remove prompt for comp name"
        )


class ExportTrackingCamera(GenericRunAction):
    ICON = ("icons.libreflow", "blender")

    _file = flow.Parent()
    _task = flow.Parent(3)
    _tasks = flow.Parent(4)

    revision = flow.Param(None, FileRevisionNameChoiceValue)

    def allow_context(self, context):
        return (
            context and len(self._file.get_revision_names(sync_status="Available")) > 0
        )

    def needs_dialog(self):
        return True

    def runner_name_and_tags(self):
        return "Blender", []

    def get_run_label(self):
        return "Export Tracking Camera"

    def target_file_extension(self):
        return "blend"

    def get_buttons(self):
        self.revision.revert_to_default()
        return ["Export", "Cancel"]

    def extra_argv(self):
        # Get blender revision
        tracking_path = self._shot_data.get("tracking_path", None)

        # Get scene builder arguments
        jsx_path = self._shot_data.get("jsx_path", None)

        # Build Blender Python expression
        python_expr = """import bpy
bpy.ops.export.jsx(filepath='%s', include_image_planes=False, include_solids=False, ae_size=%s)""" % (
            jsx_path,
            1000,
        )

        return [
            "-b",
            tracking_path,
            "--addons",
            "io_export_after_effects",
            "--python-expr",
            wrap_python_expr(python_expr),
        ]

    def _clean_jsx(self, pid):
        clean_camera = self._file.clean_camera
        clean_camera.jsx_path.set(self._shot_data.get("jsx_path", None))
        clean_camera.wait_pid(pid)
        clean_camera.run(None)

    def _ensure_file(
        self,
        name,
        format,
        path_format,
        folder=False,
        to_edit=False,
        src_path=None,
        publish_comment="",
        task=None,
        file_type=None,
    ):
        if task is None:
            task = self._task

        files = task.files
        file_name = "%s_%s" % (name, format)

        if files.has_file(name, format):
            file = files[file_name]
        else:
            self.root().session().log_info(
                "[EXPORT TRACKING CAMERA] Create tracking_camera.jsx file"
            )
            file = files.add_file(
                name=name,
                extension=format,
                tracked=True,
                default_path_format=path_format,
            )

        if not to_edit and not src_path:
            return None

        if to_edit:
            revision = file.create_working_copy(source_path=src_path)
        else:
            self.root().session().log_info(
                "[EXPORT TRACKING CAMERA] Create revision for tracking_camera.jsx"
            )
            revision = file.publish(source_path=src_path, comment=publish_comment)
            self.root().session().log_info(
                f"[EXPORT TRACKING CAMERA]    - {revision.name()}"
            )

        if file_type is not None:
            file.file_type.set(file_type)

        return file, revision.get_path()

    def get_path_format(self, task_name, file_mapped_name):
        mng = self.root().project().get_task_manager()
        if not mng.default_tasks.has_mapped_name(task_name):  # check default task
            # print(f'Scene Builder - no default task {task_name} -> use default template')
            return None

        dft_task = mng.default_tasks[task_name]
        if not dft_task.files.has_mapped_name(file_mapped_name):  # check default file
            # print(f'Scene Builder - default task {task_name} has no default file {filename} -> use default template')
            return None

        dft_file = dft_task.files[file_mapped_name]
        return dft_file.path_format.get()

    def run(self, button):
        if button == "Cancel":
            return

        self._shot_data = {}

        # Get blender revision
        rev = self._file.get_revision(self.revision.get())
        self._shot_data["tracking_path"] = rev.get_path()

        # Configure jsx file
        jsx_file, jsx_path = self._ensure_file(
            name="tracking_camera",
            format="jsx",
            path_format=self.get_path_format(self._task.name(), "tracking_camera_jsx"),
            src_path=resources.get("file_templates", "template.jsx"),
            publish_comment="Export from Blender",
            file_type="Outputs",
        )
        jsx_path = jsx_path.replace("\\", "/")
        self._shot_data["jsx_path"] = jsx_path

        if self._tasks["compositing"].file_refs.has_ref(jsx_file.oid()) is False:
            self.root().session().log_info(
                "[EXPORT TRACKING CAMERA] Link tracking_camera.jsx in compositing task"
            )
            self._tasks["compositing"].file_refs.add_ref(jsx_file.oid(), "Inputs")

        result = super(ExportTrackingCamera, self).run(button)
        blender_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(result["runner_id"])
        )
        self._clean_jsx(blender_runner["pid"])


#
#       BATCH JOBS
#


class ChangeBoolStatus(flow.Action):
    JOB = None
    _item = flow.Parent()

    def allow_context(self, context):
        return False

    def needs_dialog(self):
        if (
            self.JOB == "build"
            and not getattr(self._item, self.JOB).get()
            and self._item.bg_status.get() != "done"
        ):
            return True
        else:
            return False

    def get_buttons(self):
        self.message.set("<h2>The photoshop file has not yet been finalised.</h2>")
        return ["Force", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return self.get_result(close=True)

        getattr(self._item, self.JOB).set(
            False if getattr(self._item, self.JOB).get() else True
        )
        self._item.touch()


class ChangeBoolExport(ChangeBoolStatus):
    JOB = "export"


class ChangeBoolBuild(ChangeBoolStatus):
    JOB = "build"


class CompDynamicMapItem(flow.Object):
    _comp_map = flow.Parent()

    change_bool_export = flow.Child(ChangeBoolExport)
    change_bool_build = flow.Child(ChangeBoolBuild)

    shot = flow.Computed()
    sequence = flow.Computed()
    rendering_status = flow.Computed()
    color_status = flow.Computed()
    bg_status = flow.Computed()
    export = flow.BoolParam()
    build = flow.BoolParam()

    def compute_child_value(self, child_value):
        if child_value is self.shot:
            self.shot.set(
                self._comp_map._shot_ready[self.name()]["shot"]
            )
        elif child_value is self.sequence:
            self.sequence.set(
                self._comp_map._shot_ready[self.name()]["sequence"]
            )
        elif child_value is self.rendering_status:
            self.rendering_status.set(
                self._comp_map._shot_ready[self.name()]["rendering_status"]
            )
        elif child_value is self.color_status:
            self.color_status.set(
                self._comp_map._shot_ready[self.name()]["color_status"]
            )
        elif child_value is self.bg_status:
            self.bg_status.set(
                self._comp_map._shot_ready[self.name()]["bg_status"]
            )


class CompDynamicMap(flow.DynamicMap):
    send_comp_job_action = flow.Parent()

    def __init__(self, parent, name):
        super(CompDynamicMap, self).__init__(parent, name)
        self._shot_ready = {}

    def touch(self):
        self._shot_ready = {}
        super(CompDynamicMap, self).touch()

    @classmethod
    def mapped_type(cls):
        return CompDynamicMapItem

    def mapped_names(self, page_num=0, page_size=None):
        kitsu = self.root().project().kitsu_api()

        if len(self._shot_ready.keys()) > 0:
            return self._shot_ready.keys()

        # Get sequences, shots, and status task for rendering, color and background
        sequences = kitsu.get_sequences_data()
        for sequence in sequences: 
            shots = kitsu.get_shots_data(sequence)
            for shot in shots:
                sequence_name = sequence["name"]
                shot_name = shot["name"]
                task_rendering = kitsu.get_shot_task(
                    sequence_name, shot_name, "Rendering"
                )
                task_color = kitsu.get_shot_task(sequence_name, shot_name, "Color")
                task_bg = kitsu.get_shot_task(sequence_name, shot_name, "Background")

                # Check condition to initialize the dynamic map
                if (
                    task_rendering["task_status"]["short_name"] == "ready"
                    or (
                        task_rendering["task_status"]["short_name"] == "done"
                        and self.send_comp_job_action.load_done_shots.get() is True
                    )
                    and task_color["task_status"]["short_name"] == "done"
                ):
                    self._shot_ready[f"{sequence_name}_{shot_name}"] = {
                        "sequence": sequence_name,
                        "shot": shot_name,
                        "rendering_status": task_rendering["task_status"]["short_name"],
                        "color_status": task_color["task_status"]["short_name"],
                        "bg_status": task_bg["task_status"]["short_name"],
                    }

        return self._shot_ready.keys()

    def _configure_child(self, child):
        child.export.set(False)
        child.build.set(False)
        if child.color_status.get() == "done":
            child.export.set(True)
        if child.bg_status.get() == "done":
            child.build.set(True)
        if child.rendering_status.get() == "done":
            child.export.set(False)
            child.build.set(False)

    def columns(self):
        return ["Sequence", "Shot", "Rendering", "Export", "Build"]

    def _fill_row_cells(self, row, item):
        row["Sequence"] = self._shot_ready[item.name()]["sequence"]
        row["Shot"] = self._shot_ready[item.name()]["shot"]
        row["Rendering"] = self._shot_ready[item.name()]["rendering_status"]
        row["Export"] = ""
        row["Build"] = ""

    def _fill_row_style(self, style, item, row):
        style["Export_activate_oid"] = item.change_bool_export.oid()
        style["Build_activate_oid"] = item.change_bool_build.oid()

        style["Export_icon"] = ("icons.status", "DONE" if item.export.get() else "NONE")
        style["Build_icon"] = ("icons.status", "DONE" if item.build.get() else "NONE")


class SendCompJob(flow.Action):
    """Action who send the job export tvpaint layer and build compositing file
    Change status of Rendering and Compositing task to GO_ON on kitsu
    Download files if there aren't on the LFS site and the exchange server
    """

    _film = flow.Parent()

    load_done_shots = flow.SessionParam(False).ui(editor="bool").watched()
    comp_map = flow.Child(CompDynamicMap)

    pool = flow.Param("default", SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor="int")
    site_name = None

    def child_value_changed(self, child_value):
        if child_value is self.load_done_shots:
            self.comp_map.touch()

    def allow_context(self, context):
        return context

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set("<h2>Submit jobs to pool</h2>")
        self.pool.apply_preset()
        return ["Run", "Cancel"]

    def _get_job_label(self, entity, job_name, revision=None):
        # change the label depending on the entity

        settings = get_contextual_dict(entity, "settings")
        entity_label = [
            settings["project_name"],
            settings["sequence"],
            settings["shot"],
            settings["task"],
        ]
        if job_name == "export":
            entity_label.extend([settings["file_display_name"], revision.name()])
            label = f"TVPaint Export Layers - {' '.join(entity_label)}"
        else:
            label = f"Init Comp Scene - {' '.join(entity_label)}"

        return label

    # Change the status for rendering and compositing task on kitsu
    def change_status_task(self, _sequence, _shot, _task, _message):
        kitsu = self.root().project().kitsu_api()

        task_status = kitsu.get_shot_task(_sequence, _shot, _task)
        if task_status["task_status"]["short_name"] != "ON_HOLD":
            kitsu.set_shot_task_status(
                _sequence,
                _shot,
                _task,
                "ON_HOLD",
                f"un job {_message} a été envoyé sur le site {self.site_name}, sur le pool {self.pool.get()}",
            )

    # Download files if there are on the LFS site and on the exchange server
    def download_revision(self, _entity):
        revision = _entity.get_head_revision()
        if (
            revision.get_sync_status() != "Available"
            and revision.get_sync_status(exchange=True) == "Available"
        ):
            print(f"File has not been finalized for {_entity.oid()}")
            revision.download.run("Confirm")
            while revision.get_sync_status() != "Available":
                time.sleep(1)
            return revision
        else:
            return revision

    def check_waited_jobs(self, job_name, entity, revision=None):
        waited_jobs = [job for job in entity.jobs.mapped_items() if job.status.get() == "Wait"]

        if job_name == "export" and revision:
            jobs_revisions = [job for job in waited_jobs if job.revision.get() == revision.name()]
            if len(jobs_revisions) > 0:
                return True
        elif len(waited_jobs) > 0:
            return True

        return False

    def submit_job(self, entity, job_type, job_name, task_file=None):
        self.site_name = self.root().project().get_current_site().name()
        revision = self.download_revision(entity if job_name == "export" else task_file)

        if not self.check_waited_jobs(job_name, entity=entity, revision=revision) and revision:
            job = entity.jobs.create_job(job_type=job_type)
            if job_name == "export":
                job.revision.set(revision.name())
            # Send job
            job.submit(
                pool=self.site_name + "_" + self.pool.get(),
                priority=self.priority.get(),
                label=self._get_job_label(
                    entity, job_name, revision if job_name == "export" else None
                ),
                creator=self.root().project().get_user_name(),
                owner=self.root().project().get_user_name(),
                paused=False,
                show_console=False,
            )
            return job

        return None

    def run(self, button):
        job_type_name = ""
        if button == "Cancel":
            return

        if button == "Run":
            for entity_name in self.comp_map._shot_ready.keys():
                sequence = self.comp_map.get_mapped(entity_name).sequence.get()
                shot = self.comp_map.get_mapped(entity_name).shot.get()

                shot_entity = (
                    self.root()
                    .project()
                    .films["_2h14"]
                    .sequences[sequence]
                    .shots[shot]
                )

                # Run jobs
                if self.comp_map.get_mapped(entity_name).export.get():
                    # check if the color.tvpp file is created
                    lf_color_task = shot_entity.tasks["color"]
                    if lf_color_task.files.has_file("color", "tvpp"):
                        # Get the file path as parent
                        _file = lf_color_task.files["color_tvpp"]
                        job_type_name = "export"
                        job_export = self.submit_job(
                            entity=_file,
                            job_type=ExportTVPaintLayersJob,
                            job_name=job_type_name,
                        )

                        # change status kitsu to 'GO_ON' for rendering task
                        self.change_status_task(sequence, shot, "Rendering", "d'export")
                if self.comp_map.get_mapped(entity_name).build.get():
                    job_type_name = "build"

                    # check if the background.psd file is created
                    lf_bg_task = shot_entity.tasks["background"]
                    if lf_bg_task.files.has_file("background", "psd"):
                        # Get the file path as parent
                        _file = lf_bg_task.files["background_psd"]
                        _task = shot_entity.tasks["compositing"]
                        job_build = self.submit_job(
                            entity=_task,
                            job_type=InitCompSceneJob,
                            job_name=job_type_name,
                            task_file=_file,
                        )

                        if job_build is None:
                            print("The file isn't created")
                            continue

                        # change status kitsu to 'GO_ON' for compositing task
                        self.change_status_task(sequence, shot, "Compositing", "de build")

                    else:
                        print("The background file is not exist !")
                        continue

                if (
                    self.comp_map.get_mapped(entity_name).export.get()
                    and self.comp_map.get_mapped(entity_name).build.get()
                ):
                    # linked between export job and build job to start the build jo after the export job done
                    LinkedJob.link_jobs(job_export, job_build)
                    self.root().session().cmds.Jobs.set_job_paused(
                        job_export.job_id.get(), False
                    )
            self.comp_map.touch()


def kitsu_status_end_process(parent):
    if isinstance(parent, Task):
        r = flow.Child(KitsuStatusEndProcess)
        r.name = "kitsu_status_end_process"
        r.index = None
        return [r]


def change_kitsu_status(parent):
    if isinstance(parent, Task):
        r = flow.Child(ChangeKitsuStatus)
        r.name = "change_kitsu_status"
        r.index = None
        return [r]


def send_comp_job(parent):
    if isinstance(parent, Film) and "_2h14" in parent.name():
        send_comp_scene = flow.Child(SendCompJob).ui(dialog_size=(600, 450))
        send_comp_scene.name = "send_comp_scene"
        send_comp_scene.index = 100

        return [send_comp_scene]


def export_tracking_camera(parent):
    if (
        isinstance(parent, TrackedFile)
        and (parent.name().endswith("_blend"))
        and (parent._task.name() == "tracking")
    ):
        export_camera = flow.Child(ExportTrackingCamera)
        export_camera.name = "export_camera"
        export_camera.index = 32

        clean_camera = flow.Child(CleanTrackingJSX)
        clean_camera.name = "clean_camera"
        clean_camera.index = None
        return [export_camera, clean_camera]


def check_scene(parent):
    if isinstance(parent, TrackedFile) and "comp" in parent.name():
        check_scene = flow.Child(CompDependenciesCheck).ui(dialog_size=(650, 450))
        check_scene.name = "check_scene_dependencies"
        check_scene.index = None
        return [
            check_scene,
        ]


def build_scene(parent):
    if isinstance(parent, Task) and "comp" in parent.name():
        init_comp_scene = flow.Child(InitCompScene).ui(dialog_size=(600, 450))
        init_comp_scene.name = "init_comp_scene"
        init_comp_scene.index = None

        submit = flow.Child(SubmitInitCompSceneJob)
        submit.name = "submit_init_comp_scene_job"
        submit.ui(hidden=True)
        return [init_comp_scene, submit]


def afterfx_render_playblast(parent):
    if (
        isinstance(parent, TrackedFile)
        and (parent.name().endswith("_aep"))
        and (parent._task.name() == "compositing")
    ):
        r = flow.Child(RenderAEPlayblastComp)
        r.name = "render_ae_playblast"
        r.ui(hidden=True)
        return r


def afterfx_playblast_comp(parent):
    if (
        isinstance(parent, TrackedFile)
        and (parent.name().endswith("_aep"))
        and (parent._task.name() == "compositing")
    ):
        r = flow.Child(SelectAEPlayblastComp)
        r.name = "select_ae_playblast_render_mode"
        r.ui(label="Render playblast", dialog_size=(500, 300))
        r.index = 32
        return r


def mark_sequence_preview(parent):
    if isinstance(parent, TrackedFolder) and (parent._task.name() == "compositing"):
        r = flow.Child(MarkSequencePreview)
        r.name = "mark_image_sequence"
        r.index = 55
        return r


def final_render_wait(parent):
    if isinstance(parent, TrackedFile) and (parent._task.name() == "compositing"):
        r = flow.Child(WaitFinalRender)
        r.name = "final_render_wait"
        r.ui(hidden=True)
        return r


def install_extensions(session):
    return {
        "2h14_comp": [
            send_comp_job,
            export_tracking_camera,
            check_scene,
            build_scene,
            afterfx_render_playblast,
            afterfx_playblast_comp,
            mark_sequence_preview,
            final_render_wait,
            kitsu_status_end_process,
            change_kitsu_status,
        ]
    }
