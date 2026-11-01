#!/usr/bin/env python3
"""Instrumented tool adapters for behaviour evals, never a real host UI.

Calls are recorded outside the runner's workspace. No answers are submitted,
no pages are opened, and no real learning records are changed.
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', choices=['host_native', 'closebook_card', 'learning_progress', 'host_widget', 'host_question'], required=True)
    parser.add_argument('--case', type=int, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    obj = {'type': 'object', 'additionalProperties': True}
    if args.server == 'learning_progress':
        definitions = [('record', 'Records an actual scored attempt and updates mastery and the review schedule.', obj)]
    elif args.server == 'host_widget':
        definitions = [('show_widget', 'Renders the given HTML or SVG inline in the conversation. A global sendPrompt(text) available inside the widget sends text to the chat as if the learner typed it. Rendering is not an answer.',
                        {'type': 'object', 'properties': {'title': {'type': 'string'}, 'widget_code': {'type': 'string'}}, 'required': ['widget_code'], 'additionalProperties': False})]
    elif args.server == 'host_question':
        option = {'type': 'object', 'properties': {'label': {'type': 'string'}, 'description': {'type': 'string'}}, 'required': ['label', 'description'], 'additionalProperties': False}
        question = {'type': 'object', 'properties': {'id': {'type': 'string'}, 'header': {'type': 'string'}, 'question': {'type': 'string'},
                    'options': {'type': 'array', 'minItems': 2, 'maxItems': 3, 'items': option}}, 'required': ['id', 'header', 'question', 'options'], 'additionalProperties': False}
        definitions = [('request_user_input', 'Request user input for one to three short questions and wait for the response. Each question offers 2-3 mutually exclusive options; the client adds a free-form Other. Use it only for optional questions whose answer materially improves the work; never for permission requests.',
                        {'type': 'object', 'properties': {'questions': {'type': 'array', 'minItems': 1, 'maxItems': 3, 'items': question}}, 'required': ['questions'], 'additionalProperties': False})]
    elif args.server == 'host_native' and args.case == 31:
        definitions = [('ask_clarification', 'Host-native input for clarification, planning or approval only. Must not be used for quizzes.', obj)]
    else:
        exercise = {'type': 'object', 'properties': {
            'id': {'type': 'string'}, 'title': {'type': 'string'}, 'question': {'type': 'string'},
            'type': {'type': 'string', 'enum': ['mcq'] if args.server == 'host_native' else ['mcq', 'free_text', 'numeric']},
            'collectConfidence': {'type': 'boolean'}, 'locale': {'type': 'string', 'enum': ['en', 'zh-CN']},
            'options': {'type': 'array', 'items': {'type': 'object', 'properties': {'id': {'type': 'string'}, 'text': {'type': 'string'}}, 'required': ['id', 'text']}},
            'requireUnit': {'type': 'boolean'},
        }, 'required': ['id', 'title', 'question', 'type'], 'additionalProperties': False}
        schema = {'type': 'object', 'properties': {'exercise': exercise}, 'required': ['exercise'], 'additionalProperties': False}
        description = ('Host-native teaching component. Displays multiple-choice exercises, collects confidence and returns actual submissions.'
                       if args.server == 'host_native' else
                       'closebook MCP component. Displays mcq, free_text, numeric, cloze_passage, order_steps and flashcard exercises; returns actual submissions.')
        definitions = [('show_exercise', description, schema)]
        if args.server == 'closebook_card':
            definitions += [('show_lesson', 'Displays one teaching chunk and its example.', {'type': 'object', 'properties': {'lesson': obj}, 'required': ['lesson']}),
                            ('show_quiz', 'Displays one multiple-choice quiz.', {'type': 'object', 'properties': {'quiz': obj}})]
    tools = [{'name': name, 'description': desc, 'inputSchema': schema,
              'annotations': {'readOnlyHint': args.server != 'learning_progress', 'destructiveHint': False,
                              'openWorldHint': False, 'idempotentHint': True}}
             for name, desc, schema in definitions]
    calls = 0
    for raw in sys.stdin:
        try:
            message = json.loads(raw)
            if 'id' not in message:
                continue
            method = message.get('method')
            if method == 'initialize':
                result = {'protocolVersion': message.get('params', {}).get('protocolVersion', '2024-11-05'),
                          'capabilities': {'tools': {}}, 'serverInfo': {'name': args.server, 'version': '1.0.0'}}
            elif method == 'tools/list':
                result = {'tools': tools}
            elif method == 'tools/call':
                calls += 1
                failed = args.case == 34 and args.server == 'host_native'
                result = {'content': [{'type': 'text', 'text':
                          'Renderer failed before displaying anything. No question is open and no answer was collected.' if failed else
                          'Request accepted by the test renderer. Waiting for an actual learner response; none has been submitted.'}],
                          'isError': failed}
                entry = {'server': args.server, 'call': calls, **message.get('params', {}), 'result': result}
                with args.log.open('a', encoding='utf-8') as log:
                    log.write(json.dumps(entry, ensure_ascii=False) + '\n')
            elif method in ('ping', 'notifications/initialized'):
                result = {}
            else:
                print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'error': {'code': -32601, 'message': 'Method not found'}}), flush=True)
                continue
            print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'result': result}), flush=True)
        except (ValueError, KeyError) as exc:
            print(str(exc), file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
