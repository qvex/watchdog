import * as vscode from 'vscode';
import * as backendManager from './backendManager';
import * as inlineCompletionProvider from './inlineCompletionProvider';

let outputChannel: vscode.OutputChannel;

export async function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('Watchdog');
    outputChannel.appendLine('Watchdog Learning Assistant activated');

    const config = vscode.workspace.getConfiguration('watchdog');
    const backendPort = config.get<number>('backendPort', 5555);

    outputChannel.appendLine(`Backend port: ${backendPort}`);

    const backendRunning = await backendManager.ensureBackendRunning(backendPort, outputChannel);

    if (!backendRunning) {
        vscode.window.showErrorMessage('Watchdog: Failed to start Python backend');
        outputChannel.appendLine('ERROR: Backend failed to start');
        return;
    }

    outputChannel.appendLine('Backend running successfully');

    inlineCompletionProvider.activate(context, backendPort, outputChannel);
    outputChannel.appendLine('Inline completion provider activated');

    outputChannel.appendLine('Watchdog ready - inline suggestions enabled!');
}

export function deactivate() {
    if (outputChannel) {
        outputChannel.appendLine('Watchdog Learning Assistant deactivating...');
    }

    backendManager.stopBackend(outputChannel);

    if (outputChannel) {
        outputChannel.appendLine('Watchdog Learning Assistant deactivated');
        outputChannel.dispose();
    }
}
