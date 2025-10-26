import * as vscode from 'vscode';
import { requestHint, HintRequest } from './httpClient';

class WatchdogInlineCompletionProvider implements vscode.InlineCompletionItemProvider {
    constructor(
        private port: number,
        private outputChannel: vscode.OutputChannel
    ) {}

    async provideInlineCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.InlineCompletionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionItem[] | null> {
        if (document.languageId !== 'python') {
            return null;
        }

        const line = document.lineAt(position.line);
        const lineText = line.text.trim();
        const currentLine = line.text;
        const textAfterCursor = currentLine.substring(position.character).trim();
        const textBeforeCursor = currentLine.substring(0, position.character);
        const fullContext = document.getText();
        const cursorLineNumber = position.line + 1;

        if (textAfterCursor.length > 0) {
            return null;
        }

        if (lineText.length > 0 && !lineText.startsWith('#') && lineText.includes('return')) {
            return null;
        }

        let changeType = 'learning_hint';

        if (lineText.startsWith('#')) {
            const commentText = lineText.replace(/^#\s*/, '');
            if (!commentText.toLowerCase().startsWith('help')) {
                return null;
            }
            changeType = 'help_comment';
        }

        if (lineText.trim().length === 0 && position.line > 0) {
            const previousLine = document.lineAt(position.line - 1).text.trim();
            if (previousLine.includes('return') || previousLine.includes('pass')) {
                return null;
            }
        }

        try {
            const request: HintRequest = {
                file_path: document.fileName,
                code_snippet: JSON.stringify({
                    full_code: fullContext,
                    current_line: currentLine,
                    text_before_cursor: textBeforeCursor,
                    line_number: cursorLineNumber,
                    is_empty_line: lineText.trim().length === 0,
                    change_type: changeType
                }),
                change_type: changeType,
                language: 'python'
            };

            const response = await requestHint(this.port, request);

            if (response.success && response.hint) {
                const cleanHint = response.hint.replace(/^```python\s*\n?/, '').replace(/\n?```\s*$/, '').trim();

                if (cleanHint.length === 0) {
                    return null;
                }

                let insertText = cleanHint;
                let insertPosition = position;

                if (changeType === 'help_comment') {
                    const lineEnd = new vscode.Position(position.line, line.text.length);
                    insertText = '\n' + cleanHint;
                    insertPosition = lineEnd;
                }

                const item = new vscode.InlineCompletionItem(
                    insertText,
                    new vscode.Range(insertPosition, insertPosition)
                );
                return [item];
            }
        } catch (error) {
            this.outputChannel.appendLine(`Inline completion error: ${error}`);
        }

        return null;
    }
}

export function activate(context: vscode.ExtensionContext, port: number, outputChannel: vscode.OutputChannel) {
    const provider = new WatchdogInlineCompletionProvider(port, outputChannel);
    const disposable = vscode.languages.registerInlineCompletionItemProvider('python', provider);
    context.subscriptions.push(disposable);
}
