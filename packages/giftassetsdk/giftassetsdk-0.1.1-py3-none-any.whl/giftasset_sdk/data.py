

def convert_params_to_url_args(params: dict):
	list_of_args = [f'{key}={value}' for key, value in params.items()]
	url_args = '&'.join(list_of_args)
	return url_args, list_of_args

def remove_keys(dictionary, keys_to_remove):
    if isinstance(keys_to_remove, str):
        keys_to_remove = [keys_to_remove]
    return {k: v for k, v in dictionary.items() if k not in keys_to_remove}