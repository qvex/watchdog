import * as vscode from 'vscode';
import { requestHint, HintRequest } from './httpClient';

class WatchdogHoverProvider implements vscode.HoverProvider {
    constructor(
        private port: number,
        private outputChannel: vscode.OutputChannel
    ) {}

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | null> {
        if (document.languageId !== 'python') {
            return null;
        }

        try {
            const line = document.lineAt(position.line);
            const lineText = line.text.trim();

            if (lineText.length === 0) {
                return null;
            }

            const request: HintRequest = {
                file_path: document.fileName,
                code_snippet: lineText,
                change_type: 'hover',
                language: 'python'
            };

            const response = await requestHint(this.port, request);

            if (response.success && response.hint) {
                const markdown = new vscode.MarkdownString();
                markdown.appendCodeblock('Watchdog Hint', 'text');
                markdown.appendText(response.hint);
                return new vscode.Hover(markdown);
            }
        } catch (error) {
            this.outputChannel.appendLine(`Hover error: ${error}`);
        }

        return null;
    }
}

export function activate(context: vscode.ExtensionContext, port: number, outputChannel: vscode.OutputChannel) {
    const provider = new WatchdogHoverProvider(port, outputChannel);
    const disposable = vscode.languages.registerHoverProvider('python', provider);
    context.subscriptions.push(disposable);
}
