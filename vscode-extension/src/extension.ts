import * as vscode from 'vscode';

let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('Watchdog');
    outputChannel.appendLine('Watchdog Learning Assistant activated');

    const config = vscode.workspace.getConfiguration('watchdog');
    const backendPort = config.get<number>('backendPort', 5555);

    outputChannel.appendLine(`Backend port: ${backendPort}`);
    outputChannel.appendLine('Ready for Python learning hints');
}

export function deactivate() {
    if (outputChannel) {
        outputChannel.appendLine('Watchdog Learning Assistant deactivated');
        outputChannel.dispose();
    }
}
