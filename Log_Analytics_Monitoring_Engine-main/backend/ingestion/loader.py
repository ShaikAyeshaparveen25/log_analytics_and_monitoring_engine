import dask.bag as db

def load_logs(file_path):
    """
    Load log file line by line using Dask Bag
    """
    return db.read_text(file_path)
