import hashlib
import json


def get_invariant_hash(obj):
    """
    Returns an MD5 hash of a JSON-serialized copy of the input object, with the 'metadata' field removed.
    This hash can be used to check if two objects are equivalent, regardless of their metadata.
    """
    
    # Copiar el objeto para evitar modificar el original
    obj_copy = obj.to_dict()

    # Eliminar el campo 'metadata' del objeto copiado
    if 'metadata' in obj_copy:
        del obj_copy['metadata']

    # Serializar el objeto en formato JSON
    json_str = json.dumps(obj_copy, sort_keys=True)

    # Generar un hash MD5 del JSON serializado
    md5_hash = hashlib.md5(json_str.encode('utf-8')).hexdigest()

    return md5_hash
