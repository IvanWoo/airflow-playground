# https://alvinalexander.com/source-code/awk-script-extract-source-code-blocks-markdown-files/
BEGIN {
    # awk doesn’t have true/false variables, so
    # create our own, and initialize our variable.
    true = 1
    false = 0
    printLine = false
}

{
    # look for /kubectl run/ to start a block and /```/ to stop a block.
    # `[:space:]*` that is used below means “zero or more spaces”.
    if ($0 ~ /^kubectl run/) {
        printLine = true
        print ""
    } else if ($0 ~ /^```[:space:]*$/) {
        printLine = false
    }
 
    if (printLine) print $0
}