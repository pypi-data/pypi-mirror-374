# qltool

*tool to print some useful stuff with ql700 brother printer*

-   It is just a wrapper around the great `ql570.c` of Asbjørn Sloth
    Tønnesen, Marc Juul and Luca Zimmermann

## Installation

``` {.bash org-language="sh"}
pip3 install qltool
```

## Usage - standard print

``` {.bash org-language="sh"}
#---------text
 rm /tmp/tmp_qrcode.png ; uv run src/qltool/main.py "Ahoj
aaa
456 8jgqy 789 456 456 " --font-size 55 --font-size 45

# ---- create QR

uv run src/qltool/main.py "ahoj
momo
123 456 789 jjj" -p -q

# -------- use any image/qrcode
uv run src/qltool/main.py "Užaj jetů" --qr /tmp/baba.png

uv run src/qltool/main.py "Už je tuná" --qr /tmp/baba.png -p
```

## Using mqtt client

``` {.bash org-language="sh"}
# DO
qltool_client # somewhere...
### examples:
export D=`date +"%H:%M:%S"`; mosquitto_pub -t qltool/print -m "hoho $D -q -p"

# blocking...
mosquitto_pub -t qltool/print -m "hoho secondline thirdline  -q "

#  NEVER USE THIS:
watch -n 10 'export D=`date +"%H:%M:%S"`; mosquitto_pub -t qltool/print -m "\"hoho asdas\" \"jeli $D\"  -q "'
```

## Org-mode inventory - broken now

If this function is somewhere in the `.emacs` configfiles ...

It selects two fields fromthe TABLE and puts -q option.

You point to a line of a table and `c-c q`{.verbatim} or
`c-c w`{.verbatim} will view/print the code for inventory.

  whatever   id            name                        owner   location
  ---------- ------------- --------------------------- ------- ----------
  123        D4-12345678   najaka blbost z inventury   Pepa    Home

and this is run
`./bin_qltool.py "id: D4-12345678; name: najaka blbost z inventury  owner:Pepa " -q`
