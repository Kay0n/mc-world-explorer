from flask import send_file, jsonify, request, session, Blueprint, current_app



blueprint = Blueprint("worlds", __name__)
def save_manager():
    return current_app.config['SAVE_MANAGER']



@blueprint.route("/worlds", methods=["GET"])
def worlds():
    worlds = save_manager().get_split_world_saves()
    return worlds



@blueprint.route('/worlds/download/<save_name>')
def download_world(save_name):
    print(f"[INFO] Downloading {save_name}")
    try:
        memory_file = save_manager().create_world_zip(save_name)
        return send_file(
            memory_file,
            download_name=f"{save_name}.zip",
            as_attachment=True,
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@blueprint.route('/worlds/rename/<save_name>', methods=["POST"])
def rename_world(save_name):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        new_name = data.get('newName')
        
        if not new_name:
            return jsonify({'error': 'New name is required'}), 400

        save_manager().rename_save(save_name, new_name)
        save_manager().flush_save_cache()
        return jsonify({'message': 'World renamed successfully'}), 200

    except Exception as e:
        print(f"Error renaming world: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500