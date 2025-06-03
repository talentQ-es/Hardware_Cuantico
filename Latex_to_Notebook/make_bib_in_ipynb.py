import bibtexparser

def write_bib_notebook(Bib_file, write_path,Plantilla_Bib):

    with open(Plantilla_Bib, 'r') as f:
        header_plantilla_bib = []
        tail_plantilla_bib = []

        tail = False
        count_source = 0
        for line in f:
            if tail == False:
                if '\"source\"' in line:
                    count_source +=1
                    if count_source > 1:
                        tail = True
                        continue
                header_plantilla_bib.append(line)

            else:
                tail_plantilla_bib.append(line)

    library = bibtexparser.parse_file(Bib_file)
    print("")
    print(f"[INFO]: Writing {write_path}")

    with open(write_path, 'w') as f_out:
        for line in header_plantilla_bib:
            f_out.write(line)


        i = 1
        for entry in library.entries:
            f_out.write('   \"source\": [\n')
            entry_type = entry.entry_type
            label = entry.key

            f_out.write('    \"' +"["+str(i)+"]<a id='"+label+"'></a>"+ '\\n",\n')
            f_out.write('    \"' +"@" + entry_type + "{" +label+ '\\n",\n')
            f_out.write('    \"\\n",\n')

            for field in entry.fields:
                #value = field.value.replace("\\\'","\\\\'")
                value = field.value.replace("\\","\\\\").replace('"',"'")

                """
                if "'" in field.value:
                    print(field.value)
                    print(value)
                """
                f_out.write('    \"' +"    "+ field.key + " = {" + value + "}"+ '\\n",\n')
            f_out.write('    \"' +"}"+ '\\n"\n')

            f_out.write('   ]\n')
            f_out.write('  },\n')
            f_out.write('  {\n')
            f_out.write('   "cell_type": "markdown",\n')
            f_out.write('   "id": "080fe82e",\n')
            f_out.write('   "metadata": {},\n')
            i +=1

        f_out.write('   "source": []\n')

        for line in tail_plantilla_bib:
            f_out.write(line)


if __name__ == "__main__":

    #Notebook_folder_path = "../Notebooks"
    Plantilla_Bib = "Plantilla_Bibliografia.ipynb"
    Bib_file = "Bibliografia.bib"
    #write_path = Notebook_folder_path + "/No_Bibliografia.ipynb"
    write_path = "No_Bibliografia.ipynb"
    write_bib_notebook(Bib_file, write_path, Plantilla_Bib)
