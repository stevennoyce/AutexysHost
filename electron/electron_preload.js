const { dialog } = require('electron').remote;

window.openFolderDialog = function() {
	console.log('Triggering Electron folder dialog.')
	return dialog.showOpenDialog({properties: ['openDirectory']});
}