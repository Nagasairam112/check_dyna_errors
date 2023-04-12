import streamlit as st
import os
import tempfile
st.set_page_config(layout="wide")
st.title("Find the errors from mes files")
st.caption("Adapted from Reno Genest script, Modified by Ram ACE for Public Distribution ")
# Get file list from user
up_files = st.file_uploader("Select multiple mes files to check:", accept_multiple_files=True)
# Create a temporary directory to store uploaded files
temp_dir = tempfile.TemporaryDirectory()
# Save each uploaded file to the temporary directory and get the path
file_paths = []
if up_files:
    for uploaded_file in up_files:
        with open(os.path.join(temp_dir.name, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(os.path.join(temp_dir.name, uploaded_file.name))

# Get the list of files in the current directory that contain "mes"
current_dir_files = [filename for filename in os.listdir() if "mes" in filename]

# Combine the two lists of file names
all_files = file_paths + current_dir_files

# st.write(f"All files: {all_files}")

# # Cleanup temporary directory when finished
# temp_dir.cleanup()

mesFiles = []
mesNames = []

n = 0
for e in all_files:
    digits = len(str(n))
    if digits == 1:
        mesNames.append("mes" + "000" + str(n))
    elif digits == 2:
        mesNames.append("mes" + "00" + str(n))
    elif digits == 3:
        mesNames.append("mes" + "0" + str(n))
    elif digits == 4:
        mesNames.append("mes" + str(n))

    n = n + 1

for e in all_files:
    for a in mesNames:
        if a in e:
            mesFiles.append(e)

# Sort the list.
mesFiles.sort()

st.subheader("Output")
with open("error.txt", "w") as errorFile:
    errorFile.write("All error messages from all mesXXXX files.\n\n")

    for e in mesFiles:
        with open(e, "r") as mes1:
            mesText = mes1.read()
            if "*** Error" in mesText:
                k=os.path.basename(e)
                st.write("Error messages found in  " + k + "\n")
                errorStartPos = mesText.find("*** Error")
                errorEndPos = mesText.rfind("*** Error")

                errorText = mesText[errorStartPos - 1:errorEndPos + 2000]

                startPos = 0

                while True:
                    endPos = errorText.find("\n", startPos, )
                    string = errorText[startPos:endPos]
                    if len(string) == 0:
                        print("\n")
                        errorFile.write("\n")
                        errorText = errorText[endPos:]
                        startPos = errorText.find("*** Error")
                        errorText = errorText[startPos - 1:]
                        startPos = 0
                        if "*** Error" not in errorText:
                            break
                    else:
                        st.write(f'<span style="color:yellow">{string}</span>',unsafe_allow_html=True)
                        errorFile.write(string)
                        errorFile.write("\n")
                        startPos = endPos + 1

st.subheader("Help on fixing some errors")
col1, col2  = st.columns(2)
with col1:
    with st.expander("Negitive volume errors"):
        st.write(""" Negative Volumes in Foams (or other soft materials)
In materials that undergo extremely large
deformations, such as soft foams, an element may become so distorted
that the volume of the element is calculated as negative.  This may
occur without the material reaching a failure criterion.  There is
an inherent limit to how much deformation a Lagrangian mesh can
accommodate without some sort of mesh smoothing or remeshing taking
place.  A negative volume calculation in LS-DYNA will cause the
calculation to terminate unless ERODE in *control_timestep is set to 1
and DTMIN in *control_termination is set to any nonzero value
in which case the  offending element is deleted and the calculation
continues.
See http://ftp.lstc.com/anonymous/outgoing/support/FAQ_kw/negvol.k.  
See also PSFAIL in *control_solid.
If PSFAIL is nonzero, ERODE is not used, rather, solid elements of part set PSFAIL
will erode based on negative volume.  Furthermore, all solids elements will be
subject to time-step-based erosion based on DTMIN.
See http://ftp.lstc.com/anonymous/outgoing/support/FAQ_kw/erode_solids_by_n…
and http://ftp.lstc.com/anonymous/outgoing/support/FAQ_kw/erode_solids_by_t… .
These two input decks require the word "case" on the execution line and run different
combinations of ERODE and PSFAIL.
Some approaches that can help to overcome negative volumes include the following.
-  Stiffen up the material stress-strain curve at large strains.  This
   approach can be quite effective. See the case study
   http://www.d3view.com/best-practices-for-modeling-recoverable-low-densi…
-  Sometimes tailoring the initial mesh to accomodate
   a particular deformation field will prevent formation of negative
   volumes.  Again, negative volumes are generally only an issue for very
   severe deformation problems and typically occur only in soft materials
   like foam.
-  Reduce the timestep scale factor.  The default of 0.9 may not be sufficient to
   prevent numerical instabilities.
-  Avoid fully-integrated solids (e.g., formulations 2,3,-1,-2) which tend to be less stable
   in situations involving large deformation or distortion.
   (The fully integrated element is less robust
   than a 1-point element when deformation is large because a negative
   Jacobian can occur at one of the integration points while the element as
   a whole maintains a positive volume.  The calculation with fully
   integrated element will therefore terminate with a negative Jacobian
   much sooner than will a 1-point element. (lpb))
-  Use the default element formulation (1 point solid) with type 4 or 5 hourglass
   control (will stiffen response).  A better choice of hourglass control for foams
   modeled with type 1 solids may be:
          type 6 HG control with coef. = 0.5 if low velocity impact,
          types 2 or 3 HG control if high velcocity impact.
   The hourglass type and hourglass coefficient may warrant modification based on
   observed hourglass modes and on reported hourglass energy in matsum.

-  Model the foam with tetrahedral
   elements using solid element formulation 10
(see http://ftp.lstc.com/anonymous/outgoing/support/FAQ_docs/dubois-foam-tet…).
-  Increase the DAMP parameter (foam model 57) to the maximum recommended value of 0.5.
-  Use optional card B of *contact to turn shooting node logic off for contacts involving foam.
-  Use *contact_interior.  
   A part set defines the parts to be treated by contact_interior.  Attribute 4 (DA4 = 5th field
   of Card 1) of the part set defines the TYPE of contact_interior used.  The default TYPE is
   1 which is recommended for uniform compression.  In version 970, solid formulation 1 elements
   can be assigned TYPE=2 which treats combined modes of shear and compression.
- If mat_126 is used, try ELFORM = 0.
- Try EFG formulation (*section_solid_EFG).  Use only where deformations are severe as this
  formulation is very expensive.  Use only with hex elements.
- An ALE approach is often a preferred approach for modeling fluids or solids undergoing
  large deformations.
- An SPH approach may be a viable alternative, although SPH is generally not recom-mended for
  situations where tensile behavior is important.""")
with col2:
    with st.expander("Segmentation violation (SIGSEGV) "):
        st.write(""" Error message (Segmentation Violation )
wikipedia: http://en.wikipedia.org/wiki/Segmentation_fault
Possible procedure for the debugging of the LS-DYNA Error:
1. Is it possible to reproduce the LS-DYNA Error?
Run the identical input with identical configurations
Compare the two runs: diff between both NODOUT and both GLSTAT files
For MPP Run: extract NODOUT from the BINOUT* via l2a
--> No comparability: Hardware problem? (cpu, memory, disk, network, ...) 
2. Identify the LS-DYNA Error
activate checknan option (*CONTROL_SOLUTION, ISNAN=1)
Check the energy progression (GLSTAT, MATSUM, if necessary SLEOUT)
Can irregularities be detected immediately before the termination?
Which structural parts are affected?
Do elements fail immediately before the termination?
check-failed –l mes*
check-failed –pid –l mes* (Which PIDs are affected?)
Which are the last messages in STDOUT / STDERR / mes00xx?
Are there any problems with viscoplasticity (VP=1, “…did not converge”)?
check-hsp d3hsp –xcon mes*
Have unreasonable contact settings been applied? (e.g. large penalties- or thickness scaling etc.)
check-hsp d3hsp –cfac
Can initial penetrations be detected? How many? How large?
e.g. check-c mes* -buc –typ –typ
Are there any problems with spot welds or tied contacts? (e.g. untied nodes = cold spot welds)
e.g. check-c mes* -select tied
Within which phase the error occurs?
Keyword processing, initialization, decomposition 1-3, solution
3. Debug-Run
Switch-off „Plotcprs“ (velocity, stress, strain … available)
Termination Cycle = <Error Cycle> - 1
investigate last plot state w.r.t. max. velocities, max. plastic strains, etc..""")
with col1:
    with st.expander("NAN Error"):
        st.write("""
How can I activate the checknan option?
Command-Line:  checknan=1
Keyword:     *CONTROL_SOLUTION, ISNAN=1
Which output is produced by checknan option?
Output to screen (e.g. jobout (STDOUT)):
*** NaN detected.  Please check message file from processor for detail.
*** Error NaN detected on processor #         30  <<<
Output to messag-files (e.g. grep ‘out-of-range‘ mes0030):
*** termination due to out-of-range forces """)
with col2:
    with st.expander("Error 70021"):
        st.write(""" Increase the memeory usage in LSRUN or use *Keyowrd memeory = <a big number>""")
with col1:
    with st.expander("Error 10246 by material Key improper formatted data"):
        st.write(""" Check the titles of the Material do not use "." in the title, insted use "_" for space or seperation""")
with col2:
    with st.expander("Instablity errors "):
        st.write("""****** Approaches to combating instability of an explicit solution **********
These tips are of a general nature and may not be appropriate in all situations.

First and foremost, use the latest production release of LS-DYNA available.
Comparing results from a newer version to an older version will 
tell you if changes/improvements to code are of significance in your situation.
Or, in some cases, very recent bugfixes may not be in the latest production release
and use of a development ("dev") version may be warranted.
Contact support@lstc.com for simple instructions on how to download LS-DYNA executables.

It helps tremendously if you can identify the source of the instability. 

Steep jumps in energy values reported in matsum or sleout can help to isolate the 
part or contact, respectively, that is responsible for the instability.

Write plot states frequently enough to see the evolution 
of the instability.  The origin of instability can often be seen by plotting velocity
vectors (Vector > Velocity in LS-PrePost).  This should offer clues into what's initiating the
instability.

Some other general tips toward resolving numerical instabilities: 

-  PRECISION

Try running a double precision LS-DYNA executable.
Comparing results from single precision and double precision (being sure to run the same 
version of each)  will tell you if precision is affecting the results.    

-  TIME STEP  
Try reducing the explicit time step scale factor TSSFAC (even if mass-scaling
is invoked with DT2MS in *CONTROL_TIMESTEP).

Reducing TSSFAC too aggressively, say to 0.1 or less, can be counterproductive, especially 
in cases where the contact stiffness is directly affected by the time step (SOFT=1 or 2).   
The point here is that the explicit analysis may not converge to a single solution as you reduce 
the time step more and more.  Experience indicates that the sweetspot for TSSFAC is generally 
between 0.5 and 0.9. (jd,11/13/19)

- ELEMENT FORMULATIONS 

For underintegrated solids or underintegrated shells,
try hourglass type 4 with a hourglass coefficient of 0.03
Or, replace underintegrated shell formulations with  shell formulation -16 having hourglass type 8.  

Shells:
If response of shells is primarily elastic, set BWC=1 and PROJ=1 (B-T shells only).
For an impact simulation involving shell elements, turn on shell bulk viscosity
by setting TYPE=-2 in *CONTROL_BULK_VISCOSITY.
Unless change in shell thickness due to inplane stretching is an important effect, 
do not turn on shell thinning, i.e., leave ISTUPD=0 in *CONTROL_SHELL.  
If thinning is important in a subset of shell parts, set ISTUPD=4 and select the 
parts where thinning is to be considered by defining PSSTUPD.
Invoke invarient node numbering for shells by setting INN=2 in *CONTROL_ACCURACY

Solids:
Avoid type 2 solids.  If you prefer an 8-point hex formulation, try type (ELFORM) -1 instead.
If using type 1 solids, use at least two elements thru the thickness of the part.
Invoke invarient node numbering for orthotropic solids by setting INN=4 in *CONTROL_ACCURACY.

- ELEMENT DELETION

Elements that become problematic due to excessive deformation or distortion can be 
deleted on-the-fly through material failure criteria or various other criteria.
The most common commands for invoking such criteria include:
   - *MAT_option (many material models include their own failure criteria). 
   - *MAT_ADD_EROSION. 
   - ERODE in *CONTROL_TIMESTEP, used together with DTMIN in *CONTROL_TERMINATION.
       can be used to delete solid elements based on a specified reduction in time step 
       or based on negative volume. 
       Similarly, see PSFAIL in *CONTROL_SOLID. 
   - *CONTROL_SHELL (see variables NFAIL1, NFAIL2, PSNFAIL, KEEPCS, DELFR, W-MODE, STRETCH). 
   - *SENSOR_CONTROL (TYPE="ELESET"). 
   - *DEFINE_ELEMENT_DEATH.
- CONTACT 

Set number of cycles between bucket sorts to zero so that
the default sort interval will be used.  If the relative velocity between
two parts in contact is exceptionally high, it may be necessary to reduce 
the bucket sort interval (for instance to 5, 2, or even 1). 

If visible contact penetrations develop during the simulation, switch to
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE or *CONTACT_AUTOMATIC_SINGLE_SURFACE
with SOFT set to 1.  Make sure the mesh takes into account thickness of
shells.  If shells are VERY thin, e.g., less than 1 mm, scale up or
set the contact thickness to a more reasonable value.

Avoid redundant contact definitions, that is, don't treat contact between 
the same two parts using more than one contact definition.

-  TYPOS

Look for mistakes (typos, inconsistent units, etc.) in material input of parts
that go unstable.

-  DAMPING

Remove all *DAMPING_GLOBAL commands or at least confirm that a reasonable 
damping coefficient is being used.

Try *DAMPING_PART_STIFFNESS with a COEF of 0.1 or 0.05,
especially in the case of shell elements.

-  PROCESS OF ELIMINATION
Debug by process of elimination, i.e, simplify your model until stability is achieved.
This will help to isolate the cause of the instability.  
     - Replace complex material models with simpler ones that you are familiar with.
     - Or, test out the questionable material models with a small model to gain confidence 
         in the use and behavior of the material model.
     - Eliminate loads and/or contacts, one by one, to identify the trigger for the instability.
- NANS

Set ISNAN=1 in *CONTROL_SOLUTION to identify node IDs where out-of-range forces first appear.
The command option "checknan=1"  or the sense switch control "swn"
can activate this option as well.
When the option is invoked, LS-DYNA will report nodes where NANs occur first
to the messag (or mes**** files), 
write a plot state and terminate the job. 
The node list can be found
in the "messag" file under  "*** termination due to out-of-range forces".
Nodes appearing in that message should be examined closely for anything 
out of the ordinary.  Following is a brief list of some thngs to consider.  
   - Is the material model of the parent elements well defined?  
   - Are there any special connections at those nodes such as nodal rigid bodies?  
   - Is contact occurring on those nodes?  
   - Is mass artificially added to the nodes with *ELEMENT_MASS?
- Warnings
Look through and think about the warning messages written to the messag or mes**** files.  
These are just warnings, but might hint at much deeper issues in the model.

- IMPLICIT

If you're using the implicit solver, apply the recommendations provided in this text file 
http://ftp.lstc.com/anonymous/outgoing/support/FAQ/implicit_guidelines 
and in the documents referenced in that text file.
 """)




