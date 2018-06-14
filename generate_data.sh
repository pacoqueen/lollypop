#!/bin/bash

# To be run in project root folder.

function generate_resource()
{
    echo '<?xml version="1.0" encoding="UTF-8"?>'
    echo '<gresources>'
    echo '  <gresource prefix="/org/gnome/Lollypop">'
    for file in data/*.css
    do
        echo -n '    <file compressed="true">'
        echo -n $(basename $file)
        echo '</file>'
    done
    for file in data/*.ui AboutDialog.ui
    do
        echo -n '     <file compressed="true" preprocess="xml-stripblanks">'
        echo -n $(basename $file)
        echo '</file>'
    done
    echo '  </gresource>'
    echo '</gresources>'
}

function generate_po()
{
    cd subprojects/lollypop-po

    ## LINGUAS: File with list of languages.
    for po in *.po; do
      echo $po | cut -d '.' -f -1
    done > LINGUAS

    ## POTFILES: File that lists all the relative path to source files that
    ##           gettext should scan.
    ls ../../data/org.gnome.Lollypop.gschema.xml ../../data/*.in > POTFILES
    ls ../../data/*.ui ../../lollypop/*.py >> POTFILES
    #ls ../../subprojects/lollypop-portal/*.py >> POTFILES
    ls ../../subprojects/lollypop-portal/*.in >> POTFILES

    ## Generate .pot file
    touch lollypop.pot  # If have just cloned, need this empty file to begin
    for file in $(cat POTFILES); do
        xgettext --from-code=UTF-8 -j $file -o lollypop.pot
    done

    ## Update .po files
    #for po in *.po; do
    #    msgmerge -N $po lollypop.pot > /tmp/$$language_new.po
    #    mv /tmp/$$language_new.po $po
    #    language=${po%.po}
    #    echo $language >>LINGUAS
    #done
}

generate_resource > data/lollypop.gresource.xml
generate_po
