const {app, BrowserWindow} = require('electron');


function createWindow() {
    window = new BrowserWindow({width: 800, height: 600});
    window.loadFile('gui/index.html');

    var {PythonShell} = require('python-shell');

    PythonShell.run('main.py', null, function (err, results) {
        if (err) throw err;
        console.log('main: ', results);
    });
}

app.on('ready', createWindow);
