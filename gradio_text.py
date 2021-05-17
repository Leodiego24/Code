import os
import gradio as gr
import pandas as pd

def greet(file_submit):
  return file_submit.name

files = [
  gr.inputs.File(file_count="single", type="file", label=None)
]
iface = gr.Interface(fn=greet, inputs=files, outputs="file")
iface.launch()