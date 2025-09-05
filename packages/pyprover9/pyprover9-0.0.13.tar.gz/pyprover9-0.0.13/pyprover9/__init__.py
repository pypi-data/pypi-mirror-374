print( "* pyprover9 by Brandon Bennett (Sept 2023)" )
print( "* a Colab front-end for Prover9 by William McCune")
print( "Version date: 2023.10.02")
print()
print( """Provides:
  pyprover9.prove( assumptions, goal )
  pyprover9.input( p9inputString )
  pyprover9.full_output()   
  pyprover9.p9file( assumptions, goal )
  pyprover9.p9download( assumptions, goal )
  pyprover9.template( "probset/probname.p9" )
  pyprover9.editor( problem="probset/probname.p9", savefile="save.p9")
""" )

from .pyprover9 import prove, input, full_output, p9file
import os

def template(fname):
    d = os.path.dirname(__file__)
    respath = os.path.join( d, "problems", fname )
    with open( respath ) as f:
        content = f.read()
    return content


from google import colab
def p9download( assumptions, goal, fname, template = None ):
    content = p9file( assumptions, goal, template=template )
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    if not fname.endswith('.p9'):
      fname += ".p9"
    path = os.path.join( 'tmp', fname )
    with open( path, "w") as f:
          f.write(content)
    colab.files.download(path)


import ipywidgets as widgets

def editor(problem=None,savefile=None):
    if problem:
      if not problem.endswith('.p9'):
        problem += ".p9"
      p9input = template(problem)
      if not savefile:
        savefile = os.path.basename(problem)
    else:
      p9input = "%% Enter p9 input file content"
      if not savefile: savefile = "save.p9"
    
    layout  = widgets.Layout(flex='0 1 auto', height='500px', min_height='200px', width='auto')
    textbox = widgets.Textarea( value=p9input, layout=layout )
    run  = widgets.Button(description="Run Prover9")
    save = widgets.Button(description="Save")
    def runP9ontext(click):
      input(textbox.value)
    def saveP9(click):
      with open( savefile, 'w') as f:
        f.write(textbox.value)
      colab.files.download(savefile)
    run.on_click(runP9ontext)
    save.on_click(saveP9)
    buttons = widgets.HBox([run, save])
    vb = widgets.VBox([textbox, buttons])
    display(vb)
    
