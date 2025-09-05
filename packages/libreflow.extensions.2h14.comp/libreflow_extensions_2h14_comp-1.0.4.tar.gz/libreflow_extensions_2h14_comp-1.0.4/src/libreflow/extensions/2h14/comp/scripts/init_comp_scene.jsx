#target AfterEffects
#include "json2.js";

// ----- Utils
function print(msg) {
    $.writeln(msg)
}
$.print = print;

ColorLabels = [];
ColorLabels[0]  = [0, 0, 0 ];	// 0. None
ColorLabels[1]  = [121/255, 058/255, 058/255 ];	// 1. Red
ColorLabels[2]  = [144/255, 138/255, 068/255 ];	// 2. Yellow
ColorLabels[3]  = [115/255, 132/255, 130/255 ];	// 3. Aqua
ColorLabels[4]  = [145/255, 124/255, 131/255 ];	// 4. Pink
ColorLabels[5]  = [115/255, 115/255, 131/255 ];	// 5. Lavender
ColorLabels[6]  = [146/255, 127/255, 109/255 ];	// 6. Peach
ColorLabels[7]  = [120/255, 130/255, 120/255 ];	// 7. Sea Foam
ColorLabels[8]  = [082/255, 093/255, 142/255 ];	// 8. Blue
ColorLabels[9]  = [067/255, 112/255, 068/255 ];	// 9. Green
ColorLabels[10] = [101/255, 052/255, 107/255 ];	// 10. Purple
ColorLabels[11] = [146/255, 103/255, 037/255 ];	// 11. Orange
ColorLabels[12] = [094/255, 065/255, 051/255 ];	// 12. Brown
ColorLabels[13] = [152/255, 085/255, 137/255 ];	// 13. Fuchsia
ColorLabels[14] = [061/255, 111/255, 113/255 ];	// 14. Cyan
ColorLabels[15] = [114/255, 105/255, 090/255 ];	// 15. Sandstone
ColorLabels[16] = [045/255, 062/255, 045/255 ];	// 16. DarkGreen

TVPBlendingModes = {
    'Color': BlendingMode.NORMAL,
    'Add': BlendingMode.ADD,
    'Shade2': BlendingMode.COLOR_BURN,
    'Screen': BlendingMode.SCREEN,
    'Difference': BlendingMode.DIFFERENCE,
    'Multiply': BlendingMode.MULTIPLY,
    'Overlay': BlendingMode.OVERLAY,
	'Sub': BlendingMode.SUBTRACT,
    'Light:': BlendingMode.LUMINOSITY
};

function getFolder(path, create) {
    path = path.replace(/^\/+/, "");
    path = path.replace(/\/+$/, "");
    create = (typeof create !== 'undefined') ? create : false;

    var folderNames = path.split("/");

    if (folderNames.length == 0)
        return null;

    var folderName = folderNames[0];
    var folder = null;
    var parent = null;

    for (var i = 1; i <= app.project.items.length; i++) {
        if (app.project.items[i].name == folderName && app.project.items[i] instanceof FolderItem) {
            parent = app.project.items[i];
            break;
        }
    }

    if (parent == null && create) {
        parent = app.project.items.addFolder(folderName);
    }

    folder = parent;

    for (var i = 1; folder !== null && i < folderNames.length; i++) {
        folder = null;

        for (var j = 1; j <= parent.numItems; j++) {
            if (parent.items[j].name == folderNames[i] && parent.items[j] instanceof FolderItem) {
                parent = parent.items[j];
                folder = parent;
                break;
            }
        }
        if (folder == null && create) {
            folder = app.project.items.addFolder(folderNames[i]);
            folder.parentFolder = parent;
            parent = folder;
        }
    }

    return folder;
}

function getComp(compName) {
    comp = null;

    for (var i = 1; i <= app.project.numItems; i++) {
        if (app.project.items[i].name == compName && app.project.items[i] instanceof CompItem) {
            comp = app.project.items[i];
            break;
        }
    }

    return comp;
}

function updateCompDuration(comp, duration) {
    comp.duration = duration;

    for (var i = 1; i <= comp.numLayers; i++) {
        var layer = comp.layer(i);
        
        // Update in and out points of footages since their duration is read-only
        // From https://stackoverflow.com/a/41543354
        if (layer.source instanceof CompItem) {     // Composition
            updateCompDuration(layer.source, duration);
        }
        layer.outPoint = layer.inPoint + duration;
    }
}

function SortLinkIndex( iLink )
{
	var nLinkEntries = iLink.length;
    
    for( var i = 0; i < nLinkEntries; i++ )
	{
		iLink[i].naturalIndex = i;
		iLink[i].sortedIndex = i;
    }
}

function ReadFromData( iJsonObject, iPath, iDefaultValue )
{
	var splitPath = iPath.split( "." );

	if( splitPath == "" )
	{
		return iJsonObject;
	}
	else
	{
		if( iJsonObject.hasOwnProperty( splitPath[0] ) )
		{
			var subJsonObject = iJsonObject[splitPath[0]];
			splitPath.shift();
			var recursePath = splitPath.join( "." );

			return ReadFromData( subJsonObject, recursePath, iDefaultValue );
		}
		else
		{
			return iDefaultValue;
		}
	}
}

function ReadIntFromData( iJsonObject, iPath, iDefaultValue )
{
	return parseInt( ReadFromData( iJsonObject, iPath, iDefaultValue ) );
}

function ReadFloatFromData( iJsonObject, iPath, iDefaultValue )
{
	return parseFloat( ReadFromData( iJsonObject, iPath, iDefaultValue ) );
}

function ReadStringFromData( iJsonObject, iPath, iDefaultValue )
{
	return ReadFromData( iJsonObject, iPath, iDefaultValue );
}

function ReadArrayFromData( iJsonObject, iPath )
{
	return ReadFromData( iJsonObject, iPath, null );
}

function mathGetLength ( value1, value2 )
{
	if (typeof value1 !== typeof value2)
	{
		return null;
	}
	if (value1.length > 0)
	{
		var result = 0;
		for (var dim = 0;dim<value1.length;dim++)
		{
			result += (value1[dim]-value2[dim])*(value1[dim]-value2[dim]);
		}
		result = Math.sqrt(result);
		return result;
	}
	else return Math.abs(value1 - value2) ;
}

function autoDuration( layer, preExpression ) {
    if ( typeof preExpression === 'undefined' ) preExpression = false;

    var comp = layer.containingComp;

    var inPoint = layer.inPoint;
    var outPoint = layer.outPoint;
    var inFrame = inPoint / comp.frameDuration;
    var outFrame = outPoint / comp.frameDuration;

    //search in
    if ( layer.transform.opacity.valueAtTime( inPoint, preExpression ) == 0 ) {
        for ( var i = inFrame; i < outFrame; i++ ) {
            var time = i * comp.frameDuration;
            if ( layer.transform.opacity.valueAtTime( time, preExpression ) == 0 ) inPoint = time + comp.frameDuration;
            else break;
        }
    }

    //search out 
    if ( layer.transform.opacity.valueAtTime( outPoint, preExpression ) == 0 ) {
        for ( var i = outFrame; i > inFrame; i-- ) {
            var time = i * comp.frameDuration;
            if ( layer.transform.opacity.valueAtTime( time, preExpression ) == 0 ) outPoint = time;
            else break;
        }
    }

    //set new in and out points
    if ( inPoint != layer.inPoint ) layer.inPoint = inPoint;
    if ( outPoint != layer.outPoint ) layer.outPoint = outPoint;
}

function removeAnim( prop, removeExpression ) {
    while ( prop.numKeys > 0 ) {
        prop.removeKey( 1 );
    }
    if ( removeExpression && prop.canSetExpression ) {
        prop.expression = '';
    }
}

function setBlendingMode( layer, blendName )
{
    if ( typeof TVPBlendingModes[ blendName ] !== 'undefined' ) layer.blendingMode = TVPBlendingModes[ blendName ];
}

function setColorLabel( item, color )
{
    var smallestDistance = 1000;
    var aeLabel = 0;
    for (var l = 0, numLabels = ColorLabels.length; l < numLabels; l++)
    {
        var distance = mathGetLength( color, ColorLabels[l] );
        if (distance < smallestDistance)
        {
            smallestDistance = distance;
            aeLabel = l;
        }
    }
    item.label = aeLabel;
}

function getPrecompExposure( precomp )
{
	//get source comp
	var comp = precomp.source;

	// //add slider
	// var slider = precomp.Effects.addProperty("ADBE Slider Control");
	// slider.name = "Detected Exposure";

	//detect exposure
	for (var i = 1 ; i <= comp.numLayers ; i++)
	{
		var layer = comp.layer(i);
		// slider(1).setValueAtTime(precomp.startTime + layer.inPoint,layer.inPoint);
		// slider(1).setInterpolationTypeAtKey(slider(1).numKeys,KeyframeInterpolationType.HOLD,KeyframeInterpolationType.HOLD);
		precomp.marker.setValueAtTime(precomp.startTime + layer.inPoint,new MarkerValue(''));
	}
}

function updateBackgroundSources(backgroundPath, duration) {
    var bgSourcesFolder = getFolder("BG");
    var preCompFolder = getFolder("PRECOMPS");

    // Add background scene as composition
    var file = File(backgroundPath);
    var bgSourceCompName = file.name.substring(0, file.name.lastIndexOf('.'));
    var io = new ImportOptions(file);
    io.importAs = ImportAsType.COMP;
    var bgSourceComp = app.project.importFile(io);
    bgSourceComp.parentFolder = preCompFolder;
    setColorLabel(bgSourceComp, [067/255, 112/255, 068/255]);

    updateCompDuration(bgSourceComp, duration); // Update duration of composition and all its footages

    // Add background layers
    var bgLayersFolder = getFolder(bgSourceComp.name + " Calques");
    if (bgLayersFolder == null) {
        bgLayersFolder = getFolder(bgSourceComp.name + " Layers");
    }

    bgSourceComp.name = bgSourceCompName;
    bgLayersFolder.name = bgSourceCompName;

    if (bgLayersFolder !== null) {
        bgLayersFolder.parentFolder = bgSourcesFolder;
        setColorLabel(bgLayersFolder, [067/255, 112/255, 068/255]);
    }

    return bgSourceComp;
}


function setupScene(baseCompName, width, height, fps, duration) {
    app.beginUndoGroup("Import Setup");
    // var cameraFolder = getFolder("CAMERA", true);
    // var _3dFolder = getFolder("3D FOLDER", true);

    // Create comps
    if (duration == 0) {
        var duration = 1;
    }

    // Rename existing comps
    var mainComp = getComp('sqXXX_shXXXX');
    mainComp.name = baseCompName;
    updateCompDuration(mainComp, duration / fps);

    var mainPreComp = getComp('sqXXX_shXXXX_compositing');
    mainPreComp.name = baseCompName + "_compositing";

    app.endUndoGroup();
}

function importPSDBackground(backgroundPath, fps, duration, baseCompName) {
    app.beginUndoGroup("Import PSD Background");

    // Import background sources
    var bgSourceComp = updateBackgroundSources(backgroundPath, duration / fps);

    // Hide guide layers
    for (var i = bgSourceComp.numLayers; i > 0; i--) {
        var bgLayer = bgSourceComp.layers[i];

        if (bgLayer.name.match(/.*(FRAME|ANIMATIC|LAYOUT).*/)) {
            bgLayer.label = 0;
            bgLayer.guideLayer = true;
            bgLayer.enabled = false;
        }
    }

    // Add to main precomp
    var mainPreComp = getComp(baseCompName + '_compositing');
    var backgroundLayer = mainPreComp.layers.add(bgSourceComp);
    backgroundLayer.moveToEnd();

    app.endUndoGroup();
}

function importAnimatic(animaticPath, baseCompName) {
    app.beginUndoGroup("Import Animatic");

    var file = File(animaticPath);
    var io = new ImportOptions(file);
    var animaticFile = app.project.importFile(io);
    animaticFile.parentFolder = getFolder("REFS");

    var mainPreComp = getComp(baseCompName + '_compositing');

    if (mainPreComp !== null) {
        antcLayer = mainPreComp.layers.add(animaticFile);
        antcLayer.name = "animatic_edit";
        antcLayer.label = 0;
        antcLayer.enabled = false;
        antcLayer.audioEnabled = true;
        res_factor = mainPreComp.width / animaticFile.width
        antcLayer.property("scale").setValue([res_factor*100, res_factor*100, 0.0]);
        antcLayer.moveToBeginning();
    }

    app.endUndoGroup();
}

function importAnimationLayers(layersPath, jsonName, baseCompName) {
    app.beginUndoGroup("Import TVPaint Animation Layers");

    //From TVPaint base import script
    jsonPath = layersPath + '/' + jsonName

	var dataFile = File(jsonPath);

	//Retrieve source directory
	var srcDirPath 	= dataFile.absoluteURI.split( "/" );
	srcDirPath.pop();
	srcDirPath = srcDirPath.join( "/" );
	//Read source file
	dataFile.encoding = "UTF-8";
	dataFile.open( "r" );
	var dataString 	= dataFile.read();
	dataFile.close();
	var dataFileNameWithExtension = File.decode( dataFile.name );
	var dataFileName = dataFileNameWithExtension.split(".")[0];

    var dataTree   	= JSON.parse(dataString);

    // Comp data
	var compName   		= baseCompName + "_animation"
	var compWidth  		= ReadIntFromData( dataTree, "project.clip.width", 800 );
	var compHeight 		= ReadIntFromData( dataTree, "project.clip.height", 600 );
	var compPixelAspect = ReadFloatFromData( dataTree, "project.clip.pixelaspectratio", 1.0 );
	var compFramerate   = ReadFloatFromData( dataTree, "project.clip.framerate", 24.0 );
	var compImageCount  = ReadIntFromData( dataTree, "project.clip.image-count", 1 );
	var compBGR    		= ReadIntFromData( dataTree, "project.clip.bg.red", 255 );
	var compBGG    		= ReadIntFromData( dataTree, "project.clip.bg.green", 255 );
	var compBGB    		= ReadIntFromData( dataTree, "project.clip.bg.blue", 255 );
	var compBGColor  	= [ compBGR , compBGG , compBGB ];
	var compFrameTime 	= parseFloat(1)/compFramerate;
	var compDuration 	= parseFloat(compImageCount) / parseFloat( compFramerate );

	compBGColor[0] 		= compBGColor[0]/255;
	compBGColor[1] 		= compBGColor[1]/255;
	compBGColor[2] 		= compBGColor[2]/255;

    //create composition
    var animationFolder     = getFolder("ANIM");
	var rootFolder 			= app.project.items.addFolder( dataFileName );
    rootFolder.parentFolder = animationFolder;

    var preCompFolder       = getFolder("PRECOMPS");
	var root_composition 	= app.project.items.addComp(compName,
														compWidth,
														compHeight,
														compPixelAspect,
														compDuration,
														compFramerate);
    root_composition.bgColor 		= compBGColor;
	root_composition.parentFolder 	= preCompFolder;
    setColorLabel(root_composition, [146/255, 103/255, 037/255]);

    // BUILD LAYERS   
	var layersData = ReadArrayFromData( dataTree, "project.clip.layers" );
	var nbLayers = layersData.length;

    //Start reading layers and building them
    for(var i=nbLayers-1; i>=0;i--) // Loop through layers descending order.
	{
        // BUILD LAYER COMP
		// Now we create a comp for the layer, doing a fake sequence from files in layer directory.
		var currentLayerData  				= layersData[i];
		var layerStart 						= ReadIntFromData( currentLayerData, "start", 0 );
		var layerEnd   						= ReadIntFromData( currentLayerData, "end", 0 ) + 1;
		
		var currentLayerFolder 				= app.project.items.addFolder( ReadStringFromData( currentLayerData, "name", "Undefined") );
		currentLayerFolder.parentFolder 	= rootFolder;

		var layer_composition = app.project.items.addComp( 	ReadStringFromData( currentLayerData, "name", "Undefined"),
															compWidth,
															compHeight,
															compPixelAspect,
															compDuration,
															compFramerate);
		layer_composition.bgColor 		= compBGColor;
		layer_composition.parentFolder 	= rootFolder;

		var link 		= ReadArrayFromData( currentLayerData, "link" );
		var nbEntries 	= link.length;

		// Sorting the files...
        SortLinkIndex( link );

		var filesArray = [];
		for(var j=0; j<nbEntries; j++)
		{
			for( k = 0; k < nbEntries; k++ )
			{
				if( link[k].sortedIndex == j )
				{			            
					var entry = srcDirPath+"/"+ReadStringFromData( link[k], "file", "" );
					filesArray.push(entry);
				}
			}
		}

        // FILE IMPORT
        for(var j=filesArray.length-1; j>=0; j--)
        {
            var input 					= new ImportOptions();
            input.type 					= ImportAsType.FOOTAGE;
            input.file 					= File(filesArray[j]);
            input.sequence 				= false;
            input.forceAlphabetical 	= false;
            var importImage 			= app.project.importFile(input);
            importImage.parentFolder 	= currentLayerFolder;


            var ext = filesArray[j].split('.').pop();
            if( ext == "tif" || ext == "tiff" )
            {
                importImage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED
            }

            importImage 				= layer_composition.layers.add(importImage);

			//opacity
			//we first get values to set them later to improve performance
			var times = [];
			var values = [];
			for (var f = 0, numFrames = nbEntries; f < numFrames; f++)
			{
				var otherFrame = link[f];
                var filePath = srcDirPath+"/"+ReadStringFromData( otherFrame, "file", "" );
                var images = ReadArrayFromData( otherFrame, "images" );
				var opacity = 0;
				//if self, set to 100%
				if (filePath == filesArray[j]) opacity = 100;
				for (var k = 0, numOpacities = images.length; k < numOpacities; k++)
				{
					var time = (images[ k ] - layerStart) / compFramerate;
					times.push( time );
					values.push( opacity );
					//out of range
					if (opacity == 100)
					{
						if (time < importImage.inPoint) importImage.inPoint = time;
						if (time > importImage.outPoint) importImage.outPoint = time + 1/compFramerate;
					}
				}
			}

			//set opacity values
			if (times.length > 1)
			{
				importImage.transform.opacity.setValuesAtTimes(times, values);
				for (var k = 1; k <= importImage.transform.opacity.numKeys; k++)
				{
					importImage.transform.opacity.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
				}
			}

            autoDuration(importImage);

			//clean keyframes
            removeAnim(importImage.transform.opacity);
            importImage.transform.opacity.setValue(100);

        }

		// BUILD CURRENT LAYER IN MAIN COMP
		layer 			= root_composition.layers.add(layer_composition);
		layer.enabled 	= ReadStringFromData( currentLayerData, "visible", "true" );
		layer.inPoint 	= layerStart * compFrameTime;
		layer.outPoint 	= layerEnd * compFrameTime;

		//label
        var layerColorGroup = ReadArrayFromData( currentLayerData, "group" );
		var labelColor = [
            ReadIntFromData( layerColorGroup, "red", 0 )/255,
            ReadIntFromData( layerColorGroup, "green", 0 )/255,
            ReadIntFromData( layerColorGroup, "blue", 0 )/255
        ];
		//search for the closest one
        setColorLabel(layer, labelColor);

        // BLENDING MODES
		setBlendingMode(layer, ReadStringFromData( currentLayerData, "blending-mode" ) );
        
		// OPACITY
		layer.opacity.setValue( ReadFloatFromData( currentLayerData, "opacity", 255 ) / 255 * 100 );

        // EXPOSURE
        getPrecompExposure( layer );

        // TIME OFFSET
		layer.startTime = layerStart / compFramerate;
    }

    // Add animation precomp to main comp
    var mainPreComp = getComp(baseCompName + "_compositing");
    var animationLayer = mainPreComp.layers.add(root_composition);
    
    animationLayer.moveBefore(mainPreComp.layers.byName(baseCompName + "_background"));
    res_factor = mainPreComp.width / root_composition.width
    animationLayer.property("scale").setValue([res_factor*100, res_factor*100, 0.0]);

    app.endUndoGroup();
}

function updatePSDBackground(backgroundPath, fps, duration, baseCompName) {
    app.beginUndoGroup("Update PSD Background");
    //Get folder
    var bgSourcesFolder = getFolder('BG');
    //empty / delete it
    bgSourcesFolder.remove();

    bgSourcesFolder = getFolder('BG',true);

    //get current precomp
    var currentComp = getComp(baseCompName + '_background');
    //rename it (+= "_old")
    currentComp.name = currentComp.name + '_old';

    //import new folder
    //create new precomp
    importPSDBackground(backgroundPath, fps, duration, baseCompName);

    //add new precomp on top of current precomp
    var mainPreComp = getComp(baseCompName + '_compositing')
    var newCompLayer = mainPreComp.layer(baseCompName + '_background');
    var currentCompLayer = mainPreComp.layer(currentComp.name)
    newCompLayer.moveBefore(currentCompLayer)
    //delete current precomp
    currentComp.remove()

    app.endUndoGroup();
}

function updateAnimationLayers(layersPath, jsonName, baseCompName) {
    app.beginUndoGroup("Update TVPaint Animation Layers");
    //Get folder
    var animationFolder = getFolder("ANIM");
    //empty / delete it
    animationFolder.remove();

    animationFolder = getFolder("ANIM",true)

    //get current precomp
    var currentComp = getComp(baseCompName + '_animation');
    //rename it (+= "_old")
    currentComp.name = currentComp.name + '_old';

    //import new folder
    //create new precomp
    importAnimationLayers(layersPath, jsonName, baseCompName);

    //add new precomp on top of current precomp
    var mainPreComp = getComp(baseCompName + '_compositing')
    var newCompLayer = mainPreComp.layer(baseCompName + '_animation');
    var currentCompLayer = mainPreComp.layer(currentComp.name)
    newCompLayer.moveBefore(currentCompLayer)
    //delete current precomp
    currentComp.remove()

    app.endUndoGroup();
}

function openScene(scenePath){
    var file = new File(scenePath);
    if (file.exists) {
        var new_project = app.open(file);
    }
}

function saveScene(scenePath, baseCompName) {
    var finalComp = getComp(baseCompName + "_compositing");
    finalComp.openInViewer();
    app.project.save(new File(scenePath));
}
