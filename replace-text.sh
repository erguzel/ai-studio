#!/bin/sh


find . \( -type d -name .git -prune \) -o -type f -print0 | xargs -0 sed -i 's/old_text/replacement_text/g'


