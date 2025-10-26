import * as vscode from 'vscode';
import { requestHint, HintRequest } from './httpClient';

class WatchdogCodeLensProvider implements vscode.CodeLensProvider {
    constructor(
        private port: number,
        private outputChannel: vscode.OutputChannel
    ) {}

    provideCodeLenses(
        document: vscode.TextDocument,
        token: vscode.CancellationToken
    ): vscode.CodeLens[] {
        if (document.languageId !== 'python') {
            return [];
        }

        const codeLenses: vscode.CodeLens[] = [];
        const functionPattern = /^\s*(def|class)\s+(\w+)/;

        for (let i = 0; i < document.lineCount; i++) {
            const line = document.lineAt(i);
            const match = line.text.match(functionPattern);

            if (match) {
                const range = new vscode.Range(i, 0, i, 0);
                const command: vscode.Command = {
                    title: '💡 Get Learning Hint',
                    command: 'watchdog.showHint',
                    arguments: [document.uri, i]
                };
                codeLenses.push(new vscode.CodeLens(range, command));
            }
        }

        return codeLenses;
    }
}

async function showHintCommand(uri: vscode.Uri, lineNumber: number, port: number, outputChannel: vscode.OutputChannel) {
    try {
        const document = await vscode.workspace.openTextDocument(uri);
        const line = document.lineAt(lineNumber);

        const request: HintRequest = {
            file_path: document.fileName,
            code_snippet: line.text,
            change_type: 'codelens',
            language: 'python'
        };

        const response = await requestHint(port, request);

        if (response.success && response.hint) {
            vscode.window.showInformationMessage(`Watchdog: ${response.hint}`);
        }
    } catch (error) {
        outputChannel.appendLine(`CodeLens error: ${error}`);
    }
}

export function activate(context: vscode.ExtensionContext, port: number, outputChannel: vscode.OutputChannel) {
    const provider = new WatchdogCodeLensProvider(port, outputChannel);
    const providerDisposable = vscode.languages.registerCodeLensProvider('python', provider);

    const commandDisposable = vscode.commands.registerCommand(
        'watchdog.showHint',
        (uri: vscode.Uri, lineNumber: number) => showHintCommand(uri, lineNumber, port, outputChannel)
    );

    context.subscriptions.push(providerDisposable, commandDisposable);
}
