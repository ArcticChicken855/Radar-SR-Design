import pickle


def get_data_from_path(path):
    pkl = open(path, 'rb')
    data = pickle.load(pkl)
    pkl.close()
    return data


def get_all_data_from_path(path):
    data_array = []
    for file_path in path.glob("*"):
        data = get_data_from_path(file_path)
        data_array.append(data)
    return data_array
