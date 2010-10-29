#!/bin/bash

OUTDIR=../freshtml

test -r README.txt || ln -s ../README.txt
test -r NEWS.txt || ln -s ../NEWS.txt

rm -rf $OUTDIR

sphinx-build -a . $OUTDIR

cd $OUTDIR

# From: http://github.com/michaeljones/sphinx-to-github

for underscore_folder in  _*
do 
	echo "Processing matches for: " $underscore_folder

	folder_without_underscore=`echo -n $underscore_folder | sed 's/^.//'`

	for underscore_file in $( find $underscore_folder -type f )
	do
		echo "Check occurences of $underscore_file"
		file_without_underscore=`echo -n $underscore_file | sed 's/^.//'`

		for file in $( find . -type f -name "*.html" )
		do
			echo " - found $file"
			sed -i "" "s/${underscore_file//\//\/}/${file_without_underscore//\//\/}/g" $file
		done
	done

	mv $underscore_folder $folder_without_underscore
done

