import streamlit.web.bootstrap
import os

def partial_format(string, **kwargs):
  for k, v in kwargs.items():
    string = string.replace('{'+k+'}', str(v))
  return string

def list_format(*args):
    list_items = []
    for arg in args:
        if isinstance(arg, list):
            list_items.extend(arg)
        else:
            list_items.append(arg)
    return "\n\n".join(list_items)

def QATemplate():
   return [
      "The question is: {question}",
      "Your answer is:"
   ]


def run_server():
  # Get the directory of the current file
  dir_path = os.path.dirname(os.path.realpath(__file__))

  # Construct the full path for st.py assuming it's in the same directory
  st_py_path = os.path.join(dir_path, "st.py")

  # Now you can use st_py_path with streamlit
  streamlit.web.bootstrap.run(st_py_path, '', [], [])