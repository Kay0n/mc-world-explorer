from flask import render_template, jsonify, request, session, Response, Blueprint, current_app
import queue


blueprint = Blueprint("server", __name__)
def save_manager():
    return current_app.config['SAVE_MANAGER']
def mc_server():
    return current_app.config['MC_SERVER']



@blueprint.route('/server/start/<world_name>')
def start_server_route(world_name):  
    print(f"starting: {world_name}")                        
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    name, version = save_manager().split_world_name(world_name)
    success = mc_server().start_server(name, version)
    return jsonify({"success": success})



@blueprint.route('/server/stop')
def stop_server_route():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        mc_server().stop_server()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})



@blueprint.route('/server/status')
def get_status_route():
    return jsonify(mc_server().get_status())



@blueprint.route('/server-console')
def get_console_route():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return render_template('console.html')



@blueprint.route('/server-console/stream')
def stream_console():
    
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    mc_server_inst = current_app.config['MC_SERVER'] # generator causes issues with instance getter
    def generate():
        
        while True:
            try:
                line = mc_server_inst.console_queue.get(timeout=1)
                yield f'data: {{"line": "{line}"}}\n\n'
            except queue.Empty:
                yield f'data: {{"line": ""}}\n\n'  # Keep connection alive
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )



@blueprint.route('/server-console/command', methods=['POST'])
def send_command():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    command = data.get('command')
    
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    if mc_server().send_command(command):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Server is not running'}), 400
