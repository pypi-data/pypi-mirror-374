# prover9libV2.py

# This "Version date: 2023.10.01" 
# based on run_prover9 and prover9lib created for Gradescope
# adapted to provide a Colab version, p9file

## Version 0.4 changes
## Defined chomod_executable function to call before each use of prover9
## (This is to avoid cases where (for some reason) permission error was occuring.)

import os, stat, time
FOLDER  = os.path.dirname(__file__)
PROVER9 = os.path.join(FOLDER, "prover9-64")

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
    
time.sleep(1)

MAX_SECONDS = 10
DEBUG = True

import subprocess


def chmod_executable():
    os.chmod( PROVER9, stat.S_IRWXU ) # make prover9 executable

def p9file( assumptions, goal, template = None ):
    
    if type(assumptions) == list:
        assumptions = [trim_stops(a) for a in assumptions]
        assumptions = ".\n".join(assumptions)
    assumptions = trim_stops(assumptions)
    goal = trim_stops(goal)
    
    if not template:
        template = TEMPLATE
        
    template = template.replace( "__ASSUMPTIONS__", assumptions )
    template = template.replace( "__GOAL__", goal )
    return template

def prove( assumptions, goal, 
           template = None,
           show_time_info = True,
           show_exit_code = True,
           full_output = False,
           show_proof = True,
           show_errors=True, 
           timeout=MAX_SECONDS,
           explain_timeout = True,
           return_exit_code = False ):
               
    chmod_executable()

    # if type(assumptions) == list:
    #     assumptions = [trim_stops(a) for a in assumptions]
    #     assumptions = ".\n".join(assumptions)
    # assumptions = trim_stops(assumptions)
    # goal = trim_stops(goal)
        
    # INPUT = TEMPLATE
    # #EXIT_CODES = pyprover9.EXIT_CODES

    # INPUT = INPUT.replace( "__ASSUMPTIONS__", assumptions )   
    # INPUT = INPUT.replace( "__GOAL__", goal)
    
    INPUT = p9file( assumptions, goal, template=template )
    
    return input( INPUT,
                show_time_info = show_time_info,
                show_exit_code = show_exit_code,
                full_output = full_output,
                show_proof = show_proof,
                show_errors = show_errors, 
                timeout= timeout,
                explain_timeout = explain_timeout,
                return_exit_code = return_exit_code
              )


def input( INPUT,
         show_time_info = True,
         show_exit_code = True,
         full_output = False,
         show_proof = True,
         show_errors=True, 
         timeout=MAX_SECONDS,
         explain_timeout = True,
         return_exit_code = False 
         ):
             
    chmod_executable()
    
    with open( "prove.p9", 'w') as f:
        f.write(INPUT)
    if show_time_info: 
      print("Running prover9 (timeout at {}s) ...".format(timeout))
    
    f_in = open("prove.p9")
    f_out = open("prove.p9out", "w")
    f_err = open("prove.p9err", "w")
    child = subprocess.Popen( [PROVER9, "-t", str(timeout)], 
                              stdin=f_in, stdout=f_out, stderr=f_err)
    
    exit_code = child.wait(timeout + 2)
    f_in.close()
    f_out.close()
    f_err.close()
    
    if show_exit_code:
        code_name = EXIT_CODES[exit_code]
        print( f"prover9 exited with code: {exit_code} ({code_name})\n")
        
    if exit_code == 1 and show_errors == True:
        report_exit_code( exit_code )
        with open("prove.p9out") as f:
             result = f.read()
        display_errors(result)

    elif show_exit_code:
        #print("** verbose **")
        #print("Exit code", exit_code, type(exit_code))
        report_exit_code( exit_code )

    if full_output:
      full_output()
    elif exit_code == 0 and show_proof:
        proof = get_proof_from_output("prove.p9out")
        for line in proof:
          print(line)

    if explain_timeout and exit_code == 4:
      print(f"!!! Timeout after {timeout}s runtime. You could set a longer timeout time.")
        
    if return_exit_code:
      return exit_code    

def full_output():
    with open("prove.p9out") as f:
        output = f.read()
    print(output)


EXIT_CODES = {
  0 : 'MAX_PROOFS',       # 	The specified number of proofs (max_proofs) was found.
  1 : 'FATAL',            #	A fatal error occurred (user's syntax error or Prover9's bug).
  2 : 'SOS_EMPTY',        # 	Prover9 ran out of things to do (sos list exhausted).
  3 : 'MAX_MEGS',         #	The max_megs (memory limit) parameter was exceeded.
  4 : 'MAX_SECONDS',      # The max_seconds parameter was exceeded.
  5 : 'MAX_GIVEN',        #	The max_given parameter was exceeded.
  6 : 'MAX_KEPT',         #	The max_kept parameter was exceeded.
  7 : 'ACTION',           # A Prover9 action terminated the search.
101 : 'SIGINT',           #	Prover9 received an interrupt signal.
102 : 'SIGSEGV',          # 	Prover9 crashed, most probably due to a bug. 
}

def report_exit_code( exit_code, printout=True ):
    if exit_code == 0: report = ("*PROVED*") 
    if exit_code == 1: report = ("!!! SYNTAX ERROR !!!" )
    if exit_code == 2: report = ( "*SEARCH FAILED* (not provable)")
    if exit_code == 3: report = ( "! Max memory exceeded !")
    if exit_code == 4: report = ( "! Max seconds exceeded !")
    if exit_code == 5: report = ( "! Max given clauses exceeded !")
    if exit_code == 6: report = ( "! Max kept clauses exceeded !")
    if exit_code == 7: report =( "! A Prover9 action terminated search !")
    if exit_code == 101: report = ( "! Prover9 received an interrupt signal !")
    if exit_code == 102: report = ( "!! Prover9 Crashed !!")
    if printout:
        print( report )
    return report 
    
def display_errors(result):
    for line in result.split("\n"):
        if "ERROR" in line:
            print(line)

def get_proof_from_output(outfilename):
    with open(outfilename) as f:
        lines = f.readlines()
    start = None
    end = None
    for i, line in enumerate(lines):
        if "===== PROOF =====" in line:
            start = i
            break
    for i, line in enumerate(lines):
        if "===== end of proof =====" in line:
            end = i
    if start == None or end == None:
        return( ["!!! Could not find proof in output file !!!"] )
    prooflines = lines[start+1:end]
    prooflines[0] = "========== PROOF =========="
    prooflines = [line.strip() for line in prooflines]
    return( prooflines )
    

## This will remove all whitespace and full stops at end of a string.
## It will return possibly truncated string.
import re
def trim_stops(s):
    m = re.search(r"(\s|\.)*$", s)
    return s[:m.start()] 




TEMPLATE = """
% Saved by Prover9-Mace4 Version 0.5, December 2007.
% Last line is a lie. It is there to stop the Prover9-Mace4 GUI
% giving a warning when the file is loaded.
% This file was actually created by pyprover9 (BB Sept 2023)

set(ignore_option_dependencies). % GUI handles dependencies

if(Prover9). % Options for Prover9
  clear(auto).
  clear(auto_setup).
  clear(auto_limits).
  clear(auto_denials).
  clear(auto_inference).
  clear(auto_process).
  assign(eq_defs, pass).
  assign(max_seconds, 10).
  assign(max_weight, 2147483647).
  assign(sos_limit, -1).
  clear(predicate_elim).
  set(binary_resolution).
  set(paramodulation).
  set(factor).
end_if.

if(Mace4).   % Options for Mace4
  assign(max_seconds, 60).
end_if.

formulas(assumptions).
%%__PREAMBLE__

__ASSUMPTIONS__.

end_of_list.

formulas(goals).

__GOAL__.

end_of_list.
"""

AUTO_TEMPLATE = """
% Saved by Prover9-Mace4 Version 0.5, December 2007.

set(ignore_option_dependencies). % GUI handles dependencies

if(Prover9). % Options for Prover9
  assign(max_seconds, 60).
end_if.

if(Mace4).   % Options for Mace4
  assign(max_seconds, 60).
end_if.

formulas(assumptions).

__ASSUMPTIONS__.

end_of_list.

formulas(goals).

__GOAL__.

end_of_list.
"""

PREAMBLE = """
%% __TITLE__
%% __ATTRIBUTION__
%%
%% Prover9 file: __FILENAME__

%% To solve this first-order logic proof problem, you must replace
%% each of the assumption place-holders __An__ and the goal place-holder
%% __G__, with an approapriate first-order formula that captures the
%% meaning of the given English sentence.
%% 
%% Then run Prover9. 
%% If your representations are correct, it should find a Proof.
%% You can also check your representations using the Gradescope Autograder.

%% In writing the formulae, you should only use the following vocabulary:
%%
%% Logical symbols:           &  |  -  ->   <->  =  all  exists
%% Brackets and separators:   ( )  [  ]  ,  .
%% Variables:                 Whatever you like, but must be quantified.
%%
__VOCABULARY__
%%
%% Use only the specified vocabulary, otherwise the autograder will not work.
"""

HTML_TEMPLATE = """
<head>
<style>
table, th, td { border: 2px solid black; 
                border-collapse: separate;}
</style>
</head>

<body>
<a href="problem_index.html" style="text-decoration:none">
<tt>Problem Set: __PROBLEM_SET__</tt></a>

<h1> __TITLE__ </h1>
__ATTRIBUTION__
<p>

Your problem is to use <i>__LOGIC__</i> to represent the 
following example of reasoning, and use 
the <i>Prover9</i> theorem prover to prove that the
reasoning is valid.
<p>
Use the following template file to create your
Prover9 encoding of the problem:
<font size="+1">
<a href="__P9FILE__"><b><tt>__P9FILE__</tt></b></a>
</font>
<p>
<b>Marks: </b>There are two marks for each sentence,
making a total of <b>__MARKS__</b> marks.

__OUTLINE__

<h2>Problem Statement</h2>

__PROBLEM__

<h3>Non-Logical Vocabulary</h3>

__VOCABULARY__
"""
