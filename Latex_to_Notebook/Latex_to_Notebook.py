#!/usr/bin/env python3
'''

Made by davidcb98 (https://github.com/davidcb98)
Date: 13/06/2024

'''
#######################################################################################################################
### Help Message
#######################################################################################################################

def help_message():
    ayuda = """
=======================================================================================
Help Message:

 Este script convierte un archivo .tex en una serie de notebooks (uno por seccion).
 Este script debe de ejecutarse dentro de una carpeta "scripts" que contenga las plantillas.
 Los notebook se generarán en una carpeta "../Notebooks" que estará al mismo nivel que
 la carpeta donde se ejecuta el scipt. Es decir, la estructura de carpetas es:

    /.../scripts
    /.../scripts/Latex_to_Notebook.py
    /.../scripts/Plantilla_seccion.ipynb
    /.../scripts/Plantilla_Bibliografia.ipynb
    /.../Notebooks

 Parametros:

    - Primer argumento: ruta archivo .tex
    - Segundo argumento (opcional): ruta a la carpeta con las figuras
    - Tercer argumento (opcional): ruta al archivo .bib

 Ejemplos de ejecucion:

    python Latex_to_Notebook.py my_archivo_latex.tex
    python Latex_to_Notebook.py my_archivo_latex.tex Figuras my_bibliografia.bib
=======================================================================================
    """
    print(ayuda)
    exit(0)

import sys

if '--help' in sys.argv or '-h' in sys.argv:
    help_message()

#######################################################################################################################
### Imports
#######################################################################################################################

from subprocess import check_output as bash

import re
import numpy as np
import os
import shutil 
import unicodedata

from make_bib_in_ipynb import write_bib_notebook

from LtN_replaces_and_others import reemplazo_label, reemplazo_ref
from LtN_replaces_and_others import reemplazo_sec
from LtN_replaces_and_others import reemplazo_subsec
from LtN_replaces_and_others import reemplazo_chapter
from LtN_replaces_and_others import reemplazo_SubsubiIt, reemplazo_SubsubiiIt
from LtN_replaces_and_others import reemplazo_caption
from LtN_replaces_and_others import reemplazo_includegraphics
from LtN_replaces_and_others import reemplazo_textbf
from LtN_replaces_and_others import reemplazo_textit, reemplazo_href
from LtN_replaces_and_others import reemplazo_cite, split_cites, reemplazo_cite_full
from LtN_replaces_and_others import reemplazo_begin_figure, reemplazo_begin_table
from LtN_replaces_and_others import reemplazo_item
from LtN_replaces_and_others import find_title_subtitle_BeginBox, find_title_part
from LtN_replaces_and_others import delete_vspace, delete_hspace
from LtN_replaces_and_others import delete_comments
from LtN_replaces_and_others import build_i_a_in_b
from LtN_replaces_and_others import replace_start_newtheorem
from LtN_replaces_and_others import replace_end_newtheorem
from LtN_replaces_and_others import remove_capital_accents

from LtN_replaces_and_others import ErrorGenerico


#######################################################################################################################
### Rutas
#######################################################################################################################

#####################
## Archivo tex

try:
    file_name  = sys.argv[1:][0] # Obtenemos el nombre del archivo del primer argumento de la llamada
except:
    print("\033[91m[ERROR]: No se ha pasado ningún argumento\033[0m")
    help_message()

#####################
## Carpeta figuras

try:
    Figures_folder  = sys.argv[1:][1] # Obtenemos el nombre de la carpeta de figuras del segundo algumento de la llamada
    find_Fig_folder = True
except:
    find_Fig_folder = False

#####################
## Archivo .bib

try:
    bib_file  = sys.argv[1:][2] # Obtenemos el nombre del archivo bib del cercer algumento de la llamada
    find_bib_file = True
except:
    find_bib_file = False

######################
## Archivos de salida

Notebook_folder_path = "../Notebooks"
Notebook_old_folder_path = "../No_Notebooks_old"
Plantilla_section_path = "Plantilla_seccion.ipynb"
Plantilla_Bib = "Plantilla_Bibliografia.ipynb"

#######################################################################################################################
### Prints de las Rutas
#######################################################################################################################

def print_rutas(file_name, Figures_folder, bib_file, Notebook_folder_path, Plantilla_section_path, Plantilla_Bib):
    print("===========================")
    print("INPUTS PATHS:")
    print(" - TeX File  = ", file_name)

    if not os.path.exists(file_name):
        print("\033[91m[ERROR]: El archivo TeX no existe.\033[0m")
        exit(1)

    if find_Fig_folder == True:
        print(" - Figures Folder  = ", Figures_folder)

        if not os.path.isdir(Figures_folder):
            print("\033[91m[ERROR]: La carpeta de figuras no existe.\033[0m")
            help_message()
            exit(2)

    if find_bib_file == True:
        print(" - BibTeX File = ", bib_file)
        if not os.path.exists(bib_file):
            print("\033[91m[ERROR]: El archivo BibTeX no existe.\033[0m")
            help_message()
            exit(3)

    print("OUTPUT PATHS:")
    print(" - Notebooks folder = ", Notebook_folder_path)
    print("TEMPLATES PATHS:")
    print(" - Plantilla seccion = ", Plantilla_section_path)
    print(" - Plantilla bibliografía = ", Plantilla_Bib)
    print("===========================")

print_rutas(file_name, Figures_folder, bib_file, Notebook_folder_path, Plantilla_section_path, Plantilla_Bib)

################### grep "<a id='nielsen_chuang_2010'></a>" ../Notebooks/No_Bibliografia.ipynb | awk -F"[" '{print $2}' | awk -F"]" '{print $1}'

#######################################################################################################################
### Creamos el Notebook Folder.
#######################################################################################################################

## Si ya existe, lo movemos a uno _old y creamos el nuevo
if os.path.exists(Notebook_folder_path):
    if os.path.exists(Notebook_old_folder_path):
        shutil.rmtree(Notebook_old_folder_path)
    os.rename(Notebook_folder_path,Notebook_old_folder_path)

os.mkdir(Notebook_folder_path)
shutil.copy("index.md", Notebook_folder_path+"/")
#shutil.copytree(Figures_folder,Notebook_folder_path +"/"+ Figures_folder)


#######################################################################################################################
### Leemos la plantilla de las secciones
#######################################################################################################################

with open(Plantilla_section_path, 'r') as f:
    header_plantilla = []
    tail_plantilla = []

    tail = False
    count_source = 0
    for line in f:
        if tail == False:
            if '\"source\"' in line:
                count_source +=1
                if count_source > 1:
                    tail = True
                    continue
            header_plantilla.append(line)
        
        else:
            tail_plantilla.append(line)        



#######################################################################################################################
### Leemos el archivo TeX
#######################################################################################################################

#i_begin_doc = 0
#i_end_doc = 0
begin_doc_bool = False
end_doc_bool   = False

find_proof = False
find_itemize = False
find_itemize_2 = False
find_figure = False
find_subfigure = False
find_Teorema = False
find_Lemma = False
find_Corolario = False
find_Definicion = False
find_Proposicion = False
find_Ejercicio = False
find_table = False

find_mybox_green = False
find_mybox_gray2 = False
find_mybox_blue = False
find_mybox_gray = False
find_mybox_orange = False

num_line_text_file = 0

#omitir_seccion = False
omitir_en_Notebook = False




with open(file_name, 'r') as f:


    f_data = []
    i = 0
    i_part            = []
    i_chapter         = []
    i_section         = []
    titles_part_list  = []
    titles_part_dic   = {}
    labels_part_list  = []

    last_line = None
    for line in f:
        num_line_text_file += 1
        finds = [
                 find_mybox_gray2,
                 find_proof,
                 find_mybox_blue,
                 find_figure,
                 find_Teorema,
                 find_Lemma,
                 find_Corolario,
                 find_Definicion,
                 find_Proposicion,
                 find_Ejercicio,
                 find_mybox_green,
                 find_mybox_orange,
                 find_table
                 ]

        finds_2 = [find_itemize,
                   find_itemize_2]

        ###############################################################################################################
        ## Cogemos solo lo que hay entre el \\begin{document} y el \\end{document}
        ###############################################################################################################
        if begin_doc_bool == False:
            if "\\begin{document}" in line:
                begin_doc_bool = True
            else:
                continue
        if end_doc_bool == True:
            continue

        ###############################################################################################################
        ## Buscamos los comentarios con "% == "
        ###############################################################################################################
        if "% == Bibliograf" in line:
            i_bib = i
            #f_data.append(line)

            #i +=1
            last_line = line
            continue

        elif "% == Star_omitir_en_Notebook" in line:
            omitir_en_Notebook = True
        elif "% == End_omitir_en_Notebook" in line:
            omitir_en_Notebook = False

        if line == "":
            line = "\n"

        if line[0] == "%" or omitir_en_Notebook == True:
            continue



        # Eliminamos los espacios en blanco a izquierda y derecha
        # Sustituimos "\" por "\\"

        line = line.lstrip().rstrip().replace("\\","\\\\")
        line = line.replace('"','\\"')
        line = line.replace('``','\\"').replace("''",'\\"')
        line = line.replace("\\section*{", "\\section{")
        line = line.replace("\\subsection*{", "\\subsection{")
        line = line.replace("\\chapter*{", "\\chapter{")
        line = line.replace("\\part*{", "\\part{")
        line = line.replace("\\\\newpage","")


        # Eliminamos los tabuladores \t, teniendo cuidado de no eliminar los \\t
        line = re.sub(r'(?<!\\)\t','',line)

        if "\\\\vspace{" in line:
            line = delete_vspace(line)



        if line == "":
            line = "\\n"
        
        if line == "\\n":
            if last_line == "\\n":
                continue
            elif True in finds:
                line = "<br>"

                if last_line == "<br>" or last_line == "<br><br>" or last_line[-4:] == "<br>":
                    continue
                else:
                    f_data.append(line)
                    i +=1 
                    last_line = line
                    continue
            elif True in finds_2:
                continue

            else:
                f_data.append(line)
                i +=1 
                last_line = line
                continue





        line = delete_comments(line) # Eliminamos lo de despues de "%"

        ##### If's sueltos
        if "\\\\textbf{" in line:
            line = reemplazo_textbf(line)

        if "\\\\textit{" in line:
            line = reemplazo_textit(line)

        if "\\\\footnote" in line:
            message = "[Error] No puede haber \\footnote{}. Convertilos en cuadros"
            raise ErrorGenerico(f_data, line,num_line_text_file , message)
        """
        if "\\\\section{" in line:
            if "%%Omitir_seccion" in line:
                omitir_seccion = True
                print(line)
            else:
                omitir_seccion = False
                i_section.append(i)
                line = reemplazo_sec(line, nonumber = False)


        if omitir_seccion == True:
            continue
        """
        if "\\\\section{" in line:
            i_section.append(i)
            line = reemplazo_sec(line, nonumber = False)

        ###############################################################################################################
        ##### Cadena principal de elif's
        ###############################################################################################################


        #################### part/chapter/section/subsec #######################
        if "\\\\subsection{" in line:
            line = reemplazo_subsec(line, nonumber = False)

        elif "\\\\chapter{" in line:
            line = reemplazo_chapter(line, nonumber = False)
            i_chapter.append(i)

        elif "\\\\part{" in line: # or "\\part*{" in line:
            i_part.append(i)
            title_part, label_part = find_title_part(line)

            titles_part_list.append(title_part)
            labels_part_list.append(label_part)
            titles_part_dic[label_part] = title_part
            #print(title_part, label_part, titles_part_dic[label_part])


        elif "\\\\SubsubiIt{" in line:
            line = reemplazo_SubsubiIt(line)

        elif "\\\\SubsubiiIt{" in line:
            line = reemplazo_SubsubiiIt(line)

        #################### mybox_gray / Nota sin titulo #######################

        elif "\\\\begin{mybox_gray2}" in line :
            find_mybox_gray2 = True
            line = '<div class=\\"alert alert-block alert-info\\">\\n",\n' + \
                    '    "<p style=\\"color: navy;\\">\\n",\n'+ \
                    '    "<b></b>'

        elif "\\\\end{mybox_gray2}" in line:
            find_mybox_gray2 = False
            line = '</p></div>'


        #################### mybox_blue / Nota y Resumen #######################
        elif "\\\\begin{mybox_blue}" in line:
            find_mybox_blue = True
            try:
                title, subtitle = find_title_subtitle_BeginBox(line)
            except:
                message = "Error al buscar el titulo y subtitulo de una mybox_green"
                raise ErrorGenerico(f_data, line,num_line_text_file , message)


            if subtitle == None:
                line = '<div class=\\"alert alert-block alert-danger\\">\\n",\n' + \
                        '    "<p style=\\"color: DarkRed;\\">\\n",\n' + \
                        '    "<b>'+title+'</b>:\\n",\n' + \
                        '    "<br>'
            else:
                line = '<div class=\\"alert alert-block alert-danger\\">\\n",\n' + \
                        '    "<p style=\\"color: DarkRed;\\">\\n",\n' + \
                        '    "<b>'+title+'</b>: <i>('+subtitle+')</i>\\n",\n' + \
                        '    "<br>'

        elif "\\\\end{mybox_blue}" in line:
            find_mybox_blue = False
            line = '</p></div>'

        #################### mybox_green / Ejemplos #######################

        elif "\\\\begin{mybox_green}" in line:
            find_mybox_green = True
            try:
                title, subtitle = find_title_subtitle_BeginBox(line)
            except:
                message = "Error al buscar el titulo y subtitulo de una mybox_green"
                raise ErrorGenerico(f_data, line,num_line_text_file , message)

            if subtitle == None:
                line = '<div class=\\"alert alert-block alert-success\\">\\n",\n' + \
                        '    "<p style=\\"color: DarkGreen;\\">\\n",\n' + \
                        '    "<b>'+title+'</b>:\\n",\n' + \
                        '    "<br>'
            else:
                line = '<div class=\\"alert alert-block alert-success\\">\\n",\n' + \
                        '    "<p style=\\"color: DarkGreen;\\">\\n",\n' + \
                        '    "<b>'+title+'</b>: <i>('+subtitle+')</i>\\n",\n' + \
                        '    "<br>'

        elif "\\\\end{mybox_green}" in line:
            find_mybox_green = False
            line = '</p></div>'

        #################### mybox_orange / Ref a Notebooks #######################

        elif "\\\\begin{mybox_orange}" in line:
            find_mybox_orange = True
            try:
                title, subtitle = find_title_subtitle_BeginBox(line)
            except:
                message = "Error al buscar el titulo y subtitulo de una mybox_green"
                raise ErrorGenerico(f_data, line,num_line_text_file , message)

            if subtitle == None:
                line = '<div class=\\"alert alert-block alert-warning\\">\\n",\n' + \
                        '    "<p style=\\"color: #4B5320;\\">\\n",\n' + \
                        '    "<b>'+title+'</b>:\\n",\n' + \
                        '    "<br>'
            else:
                line = '<div class=\\"alert alert-block alert-warning\\">\\n",\n' + \
                        '    "<p style=\\"color: #4B5320;\\">\\n",\n' + \
                        '    "<b>'+title+'</b>: <i>('+subtitle+')</i>\\n",\n' + \
                        '    "<br>'

        elif "\\\\end{mybox_orange}" in line:
            find_mybox_orange = False
            line = '</p></div>'

        ########################### Teoremas  #############################
        elif "\\\\Teorema{" in line:
            find_Teorema = True

            i_start_teorema_in_tex   = num_line_text_file
            num_start_braket_teorema = len(re.findall(r'(?<!\\)\{', line))
            num_end_braket_teorema   = len(re.findall(r'(?<!\\)\}', line))

            line = replace_start_newtheorem(f_data, line, "Teorema", "Teorema", "info")



        elif find_Teorema == True:
            num_start_braket_teorema = len(re.findall(r'(?<!\\)\{', line)) + num_start_braket_teorema
            num_end_braket_teorema   = len(re.findall(r'(?<!\\)\}', line)) + num_end_braket_teorema

            line, find_Teorema = \
                replace_end_newtheorem(f_data, line, find_Teorema, i_start_teorema_in_tex, num_start_braket_teorema, num_end_braket_teorema, "Teorema")



        ########################### Definicion  #############################
        elif "\\\\Definicion{" in line:

            find_Definicion = True

            i_start_definicion_in_tex   = num_line_text_file
            num_start_braket_definicion = len(re.findall(r'(?<!\\)\{', line))
            num_end_braket_definicion   = len(re.findall(r'(?<!\\)\}', line))

            line = replace_start_newtheorem(f_data, line, "Definicion", "Definición", "info")


        elif find_Definicion == True:
            num_start_braket_definicion = len(re.findall(r'(?<!\\)\{', line)) + num_start_braket_definicion
            num_end_braket_definicion   = len(re.findall(r'(?<!\\)\}', line)) + num_end_braket_definicion

            line, find_Definicion = \
                replace_end_newtheorem(f_data, line, find_Definicion, i_start_definicion_in_tex, num_start_braket_definicion, num_end_braket_definicion, "Definicion")


        ########################### Lemma  #############################
        elif "\\\\Lemma{" in line:

            find_Lemma = True

            i_start_lemma_in_tex   = num_line_text_file
            num_start_braket_lemma = len(re.findall(r'(?<!\\)\{', line))
            num_end_braket_lemma   = len(re.findall(r'(?<!\\)\}', line))

            line = replace_start_newtheorem(f_data, line, "Lemma", "Lema", "info")


        elif find_Lemma == True:
            num_start_braket_lemma = len(re.findall(r'(?<!\\)\{', line)) + num_start_braket_lemma
            num_end_braket_lemma   = len(re.findall(r'(?<!\\)\}', line)) + num_end_braket_lemma

            line, find_Lemma = \
                replace_end_newtheorem(f_data, line, find_Lemma, i_start_lemma_in_tex, num_start_braket_lemma, num_end_braket_lemma, "Lemma")


        ########################### Ejercicio  #############################
        elif "\\\\Ejercicio{" in line:

            find_Ejercicio = True

            i_start_ejercicio_in_tex   = num_line_text_file
            num_start_braket_ejercicio = len(re.findall(r'(?<!\\)\{', line))
            num_end_braket_ejercicio   = len(re.findall(r'(?<!\\)\}', line))

            line = replace_start_newtheorem(f_data, line, "Ejercicio", "Ejercicio", "success")


        elif find_Ejercicio == True:
            num_start_braket_ejercicio = len(re.findall(r'(?<!\\)\{', line)) + num_start_braket_ejercicio
            num_end_braket_ejercicio   = len(re.findall(r'(?<!\\)\}', line)) + num_end_braket_ejercicio

            line, find_Ejercicio = \
                replace_end_newtheorem(f_data, line, find_Ejercicio, i_start_ejercicio_in_tex, num_start_braket_ejercicio, num_end_braket_ejercicio, "Ejercicio")

        ########################### Proposicion  #############################
        elif "\\\\Proposicion{" in line:

            find_Proposicion = True

            i_start_proposicion_in_tex   = num_line_text_file
            num_start_braket_proposicion = len(re.findall(r'(?<!\\)\{', line))
            num_end_braket_proposicion   = len(re.findall(r'(?<!\\)\}', line))

            line = replace_start_newtheorem(f_data, line, "Proposicion", "Proposición", "info")


        elif find_Proposicion == True:
            num_start_braket_proposicion = len(re.findall(r'(?<!\\)\{', line)) + num_start_braket_proposicion
            num_end_braket_proposicion   = len(re.findall(r'(?<!\\)\}', line)) + num_end_braket_proposicion

            line, find_Proposicion = \
                replace_end_newtheorem(f_data, line, find_Proposicion, i_start_proposicion_in_tex, num_start_braket_proposicion, num_end_braket_proposicion, "Proposicion")

        ########################### Corolario  #############################
        elif "\\\\Corolario{" in line:

            find_Corolario = True

            i_start_corolario_in_tex   = num_line_text_file
            num_start_braket_corolario = len(re.findall(r'(?<!\\)\{', line))
            num_end_braket_corolario   = len(re.findall(r'(?<!\\)\}', line))

            line = replace_start_newtheorem(f_data, line, "Corolario", "Corolario", "info")


        elif find_Corolario == True:
            num_start_braket_corolario = len(re.findall(r'(?<!\\)\{', line)) + num_start_braket_corolario
            num_end_braket_corolario   = len(re.findall(r'(?<!\\)\}', line)) + num_end_braket_corolario

            line, find_Corolario = \
                replace_end_newtheorem(f_data, line, find_Corolario, i_start_corolario_in_tex, num_start_braket_corolario, num_end_braket_corolario, "Corolario")

        ########################### Tablas  #############################
        elif "\\\\begin{table}" in line:
            find_table = True
            title = ""
            label = ""
            start_table = False
            num_line_begin_table = i


        elif find_table == True:
            if "\\\\end{table}" in line:
                find_table = False
                line = line.replace("\\\\end{table}",'``````\\n')
                f_data[num_line_begin_table] = reemplazo_begin_table(f_data[num_line_begin_table], title, label)

            elif "\\\\begin{tabular}" in line:
                start_table = True
                continue
            elif "\\\\end{tabular}" in line:
                start_table = False
                continue

            elif start_table == True:
                line_list = line.replace("\\\\hline","").replace("\\\\\\\\","").split("&")

                if len(line_list) == 1 and line_list[0].lstrip().rstrip() == "":
                    continue

                line = ""
                for item in line_list:
                    line += '    "  - ' + item.lstrip().rstrip() + '\\n",\n'
                line = "*" + line[6:-5]
                #print({line})

            else:

                if "\\\\caption{" in line:
                    num_start_braket_caption = len(re.findall(r'(?<!\\)\{', line))
                    num_end_braket_caption   = len(re.findall(r'(?<!\\)\}', line))


                    if num_start_braket_caption != num_end_braket_caption:
                        message = "El numero de \"{\" y \"}\" diferentes en caption de una tabla. \nLa caption debe de ir en una sola linea."
                        raise ErrorGenerico(f_data, line, num_line_text_file, message)

                    title = reemplazo_caption(line,"","")
                    continue

                        #line = ""

                elif "\\\\label{" in line:
                    label = reemplazo_label(line,"","")
                    continue
                elif "\\\\centering" in line:
                    continue
        ##################### end document #######################
        elif "\\\\end{document}" in line:
            end_doc_bool = True




        ###############################################################################################################
        ##### Otros if
        ###############################################################################################################

        ############################ Referencias #############################

        if "\\\\ref{" in line:
            #print({line})
            line = reemplazo_ref(line)
            #print({line})
            #wait = input("Press Enter to continue.")

        ############################### href #################################

        if "\\\\href{" in line:
            line = reemplazo_href(line)

        ############################ Enumerate ##############################
        if "\\\\begin{enumerate}" in line:

            message = "No se aceptan los \\begin\{enumerate\}. \n"+ \
                      "Sustituirlo con \\begin\{itemize\} usando \\item[1.], \\item[2.], ..."
            raise ErrorGenerico(f_data, line, num_line_text_file, message)

        ############################ Itemice ##############################
        if "\\\\begin{itemize}" in line:
            if find_itemize == True:
                find_itemize_2 = True
            else:
                find_itemize = True

            # Esto es para que si estamos en un cuadro, temos los <br>
            if True in finds:
                line = line.replace("\\\\begin{itemize}","<br>")
            else:
                line = line.replace("\\\\begin{itemize}","")

        elif "\\\\end{itemize}" in line:
            if find_itemize_2 == True:
                find_itemize_2 = False
            else:
                find_itemize = False

            if True in finds:
                line = line.replace("\\\\end{itemize}","<br>")
            else:
                line = line.replace("\\\\end{itemize}","")

        elif find_itemize == True:
            if "\\\\item" in line:
                if find_itemize_2 == True:
                    #line = line.replace('\\\\item', '    -')
                    line = reemplazo_item(line, '    ')
                    if True in finds:
                        line = "<br>\\n" + line
                    else:
                        line = " \\n" + line

                else:
                    #line = line.replace('\\\\item', '-')
                    line = reemplazo_item(line, '')
                    if True in finds:
                        line = "<br>\\n" + line
                    else:
                        line = " \\n" + line
            else:
                if find_itemize_2 == True:
                    line = '        ' + line
                else:
                    line = '    ' + line
            """
            if True in finds:
                line = line + '\\n",\n' + \
                            '    "<br>'
            else:
                line = line + '\\n",\n' + \
                            '    "'
            """


        ######################## proof / dropdown #########################
        if "\\\\begin{proof}" in line :
            find_proof = True
            line = line.replace("\\\\begin{proof}",'<details><summary><p style=\\"color:blue\\" > >> <i>Demostración</i> </p></summary>')

        elif "\\\\end{proof}" in line :
            find_proof = False
            line = line.replace("\\\\end{proof}",'</details>\\n')

        ############################ Figuras ##############################
        if "\\\\begin{figure}" in line :
            find_figure = True
            label_writed = False
            caption_writed = False
            caption_find = False
            #line = line.replace("\\\\begin{figure}",'<figure><center>')
            line = reemplazo_begin_figure(line).replace("\\\\setcounter{subfigure}{0}","")

        if find_figure == True:
            ## Cosas de todas las figuras
            if "\\\\end{figure}" in line :
                find_figure = False
                find_subfigure = False

                line = line.replace("\\\\end{figure}",'</center></figure>\\n')

                if caption_find == True and caption_writed == False:
                    line = line_caption + '\\n",\n' + \
                           '    "' + line


            if "\\\\centering" in line and find_figure == True:
                line = line.replace("\\\\centering","")
                continue

            if "\\\\hspace{" in line:
                line = delete_hspace(line)
                if line == '':
                    continue

            ## Ahora tratanos por separado las figuras normales de las subfigure
            if "\\\\subfigure" in line:
                find_subfigure = True

            if find_subfigure == True:
                message = "No se aceptan las subfigure. Deben sustituirse por una única figura\n" + \
                          "con un único pie de foto."
                raise ErrorGenerico(f_data, line, num_line_text_file, message)
            else:
                if "\\\\caption{" in line and find_figure == True:

                    num_start_braket_caption = len(re.findall(r'(?<!\\)\{', line))
                    num_end_braket_caption   = len(re.findall(r'(?<!\\)\}', line))

                    if num_start_braket_caption != num_end_braket_caption:
                        message = "El numero de \"{\" y \"}\" diferentes en caption de una figura. \nLa caption debe de ir en una sola linea."
                        raise ErrorGenerico(f_data, line, num_line_text_file, message)

                    caption_find = True

                    if label_writed == False:
                        line_caption = reemplazo_caption(line,"<center>","</center>")
                        continue
                        line = ""
                    else:
                        line = reemplazo_caption(line)
                        caption_writed = True


                if "\\\\includegraphics[" in line and find_figure == True and not "\\subfigure" in line:
                    line = reemplazo_includegraphics(line)

                if "\\\\label{" in line and find_figure == True:
                    line = reemplazo_label(line)
                    label_writed = True




        if "\t" in line:
            message = "Parece que ha quedado un tabulador (\\t) suelto."
            raise ErrorGenerico(f_data, {line}, num_line_text_file, message)

        f_data.append(line)
        i +=1
        last_line = line


#######################################################################################################################
# Arreglamos las referencias a las Partes sustituyendolas por el Titulo de las Partes

for i in range(len(f_data)):
    if "\\\\ref{" in f_data[i]:
        print("----------" +f_data[i])
        f_data[i] = reemplazo_ref(f_data[i], titles_part_dic)
        print("----------" +f_data[i])
        print("")

#######################################################################################################################
### Creamos el Bibliografia.ipynb
### y la variable "cites_dic"
#######################################################################################################################

if find_bib_file == True:

    bib_file_ipynb = "Bibliografia.ipynb"
    write_path_bib = Notebook_folder_path+"/" + bib_file_ipynb

    write_bib_notebook(bib_file, write_path_bib,Plantilla_Bib)   # Hacemos el Bibliografia.ipynb

    shutil.copy(bib_file, Notebook_folder_path)              # Copiamos el .bib

    # Le ponemos de nombre Bibliografia.bib
    os.rename(Notebook_folder_path+"/"+bib_file, Notebook_folder_path+"/Bibliografia.bib")

    # Del archivo que acabamos de escribir, sacamos los nombres de las referencias y los números
    bash_command = 'grep "\]<a id='+"'"+'" '+ write_path_bib + ' | sed -E "s/.*\\\"\\\\[(.*)\\\\]<a id=' + "'([^']*)'.*/\\1 \\2/" + '"'

    cites_list = bash(bash_command, shell=True).decode("utf-8").splitlines()

    # Construimos un diccionario con los nombres de las referencias como claves, y los numes como items:
    # Ejemplo:
    #   cites_dic[bib_...] = '5'

    cites_dic = {item.split()[1]: item.split()[0] for item in cites_list}



#######################################################################################################################
### Escribimos los notebook
#######################################################################################################################




def test_write_start_end(i_end_write_old, i_start_write, write_path):
    if i_end_write_old > i_start_write:
        print(f"\033[91m======\033[0m") 
        print(f"\033[91mLa anterior escritura termino después del inicio de la actual\033[0m")
        print(f"\033[91mEs decir, i_end_write_old > i_start_write: {i_end_write_old} > {i_start_write} \033[0m")
        print(f"\033[91mPath al ultimo archivo escrito: \033[0m")
        print("   ",write_path)
        print(f"\033[91m======\033[0m") 
        raise 

def write_notebook(f_data, i_start_write, i_end_write, write_path, header_plantilla, tail_plantilla, cites_dic, path_bib_ipynb):

    print(f"[INFO]: Writing {write_path}")

    reemplazo_cite_full(f_data, i_start_write, i_end_write, cites_dic, path_bib_ipynb)

    with open(write_path, 'w') as f_out:
        for line in header_plantilla:
            f_out.write(line)

        f_out.write('   \"source\": [\n')
        for k in range(i_start_write, i_end_write - 1):
            if f_data[k] == '\\n':
                f_out.write('   ]\n')
                f_out.write('  },\n')
                f_out.write('  {\n')
                f_out.write('   "cell_type": "markdown",\n')
                f_out.write('   "id": "080fe82e",\n')
                f_out.write('   "metadata": {},\n')
                f_out.write('   "source": [\n')
            #print({'    \"' +f_data[k].replace("\\","\\\\") + '\\n",\n'})
            elif f_data[k+1] == '\\n':
                f_out.write('    \"' +f_data[k]+ '\\n"\n')
            else:
                f_out.write('    \"' +f_data[k]+ '\\n",\n')
        if f_data[k+1] != '\\n':
            f_out.write('    \"' +f_data[k+1]+ '\\n\"\n')
        f_out.write('   ]\n')

        for line in tail_plantilla:
            f_out.write(line)
    
    ##################
    ### Test
    global i_end_write_old

    test_write_start_end(i_end_write_old, i_start_write, write_path)

    i_end_write_old = i_end_write
    

i_chap_in_parts, chapters_before_first_part = build_i_a_in_b(i_chapter, i_part)
i_sec_in_chap, _ = build_i_a_in_b(i_section, i_chapter)

print("")


chapters_before_first_part_aux = chapters_before_first_part
k_part = 0
k_part_sum = 0
k_chap_sum = 0
i_end_write_old = -1

for k_chap_in_one_part in i_chap_in_parts:
    if chapters_before_first_part_aux == False:
        print(f"\nPart_"+str(k_part_sum+1).zfill(2), {f_data[i_part[k_part]]})
        part_folder_path = str(Notebook_folder_path) + "/" + f"Part_"+str(k_part_sum+1).zfill(2)
        os.mkdir(part_folder_path)

        # Caption.txt
        write_path = part_folder_path + "/caption.txt"
        with open(write_path, 'w') as f_out:
            f_out.write(titles_part_list[k_part])

        shutil.copytree(Figures_folder, part_folder_path + "/" + Figures_folder)
        k_part +=1
        k_part_sum +=1
    else:
        print(f"\nPart_"+str(k_part_sum+1).zfill(2))
        part_folder_path = str(Notebook_folder_path) + "/" + f"Part_"+str(k_part_sum+1).zfill(2)
        os.mkdir(part_folder_path)

        #Caption.txt
        write_path = part_folder_path + "/caption.txt"
        with open(write_path, 'w') as f_out:
            f_out.write("")

        shutil.copytree(Figures_folder, part_folder_path + "/" + Figures_folder)
        k_part_sum +=1

    chapters_before_first_part_aux = False

    k_chap_sum_part = 0
    
    for k_chap in k_chap_in_one_part:

        #print("  ",f"Chapter_"+str(k_chap_sum +1).zfill(3), {f_data[i_chapter[k_chap]]})
        k_sec_sum = 0

        i_start_write = i_chapter[k_chap]

        title_lowecase = remove_capital_accents(f_data[i_start_write].lstrip().replace(" ","_")  \
                        .replace(":","").replace(".","").replace(">","").replace("<","").replace("\"","")        \
                        .replace("/","").replace("\\","").replace("|","").replace("?","").replace("¿","") \
                        .replace("(","").replace(")","").replace("$","").split('#_')[1])


        chapter_intro_file_path = part_folder_path + "/Chapter_"+str(k_chap_sum +1).zfill(3)+"_01_" + title_lowecase + ".ipynb"
        chapter_folder_path     = part_folder_path + "/Chapter_"+str(k_chap_sum +1).zfill(3)+"_02"



        if len(i_sec_in_chap[k_chap]) >= 1:
            ## Escribimos lo que hay antes de la primera seccion del capitulo en un archivo Chapter_.._01
            write_path = chapter_intro_file_path
            i_end_write = i_section[i_sec_in_chap[k_chap][0]]
            path_bib_ipynb = "../"+bib_file_ipynb


            write_notebook(f_data, i_start_write, i_end_write, write_path, header_plantilla, tail_plantilla, cites_dic, path_bib_ipynb)

            ## Carpeta para las secciones
            os.mkdir(chapter_folder_path)
            shutil.copytree(Figures_folder, chapter_folder_path + "/" + Figures_folder)

            ## Escribirmos las secciones
            for k_sec in i_sec_in_chap[k_chap]:
                #print("    ", f"Section_"+ str(k_sec_sum+1).zfill(3) ,i_section[k_sec], {f_data[i_section[k_sec]]})
                i_start_write = i_section[k_sec]

                title_lowecase = remove_capital_accents(f_data[i_start_write].lstrip().replace(" ","_")  \
                                .replace(":","").replace(".","").replace(">","").replace("<","").replace("\"","")        \
                                .replace("/","").replace("\\","").replace("|","").replace("?","").replace("¿","") \
                                .replace("(","").replace(")","").replace("$","").split('#_')[1])

                sec_file_path = str(chapter_folder_path) + "/" + f"Section_"+ str(k_sec_sum+1).zfill(3)+"_"+ title_lowecase + ".ipynb"
                write_path = sec_file_path
                path_bib_ipynb = "../../"+bib_file_ipynb

                if k_sec_sum < len(i_sec_in_chap[k_chap]) -1 :
                    i_end_write   = i_section[k_sec + 1]
                    
                    
                else:
                    if k_chap_sum_part < len(k_chap_in_one_part) - 1:
                        i_end_write   = i_chapter[k_chap + 1]

                    else:
                        if k_part == k_part_sum:
                            k_part_aux = k_part + 1
                        else:
                            k_part_aux = k_part 

                        if k_part_aux < len(i_part):
                            i_end_write = i_part[k_part_aux]
                        else:
                            i_end_write = i_bib

                write_notebook(f_data, i_start_write, i_end_write, write_path, header_plantilla, tail_plantilla, cites_dic, path_bib_ipynb)
                k_sec_sum += 1
        else:
            ## Escribimos lo que hay antes de la primera seccion del capitulo en un archivo Chapter_.._01
            write_path = chapter_intro_file_path
            path_bib_ipynb = "../"+bib_file_ipynb

            if k_chap_sum_part < len(k_chap_in_one_part) - 1:
                i_end_write   = i_chapter[k_chap + 1]

            else:
                if k_part == k_part_sum:
                    k_part_aux = k_part + 1
                else:
                    k_part_aux = k_part 

                if k_part_aux < len(i_part):
                    i_end_write = i_part[k_part_aux]
                else:
                    i_end_write = i_bib

            write_notebook(f_data, i_start_write, i_end_write, write_path, header_plantilla, tail_plantilla, cites_dic, path_bib_ipynb)


            
        

        k_chap_sum +=1
        k_chap_sum_part += 1


#for i in range(7642, 7642+10):
#    print({f_data[i]})

print("")
print_rutas(file_name, Figures_folder, bib_file, Notebook_folder_path, Plantilla_section_path, Plantilla_Bib)
