# Usar grep para encontrar las líneas con "\ref" y el número de línea

if [ -z $1 ]; then
	echo "Hay que pasarle un archivo como argumento"
	exit 1
fi

grep -n "\\\\ref{" $1 | awk '
{
    # Separar la línea en número de línea y contenido
    split($0, arr, ":")
    line_number = arr[1]
#    line_content = arr[2]
#    line_number = $1
    sub(/^[0-9]+:/, "", $0)
    line_content = $0

    # Usar split para dividir la línea en palabras
#    n = split(line_content, words, " ")

    # Iterar sobre las palabras y encontrar las que contienen "ref{"
#    for (i = 1; i <= n; i++) {
#        if (words[i] ~ /ref{/) {
#            print line_number, words[i]
#        }
    while (match(line_content, /\\ref\{[^}]*\}/)) {
        ref = substr(line_content, RSTART + 5, RLENGTH - 6)
        print line_number, ref
        # Remover la ocurrencia actual para buscar la siguiente en la línea
        line_content = substr(line_content, RSTART + RLENGTH)
   
    }
}' | sed "s/(//g" | sed "s/)//g" | sed "s/,//g"

