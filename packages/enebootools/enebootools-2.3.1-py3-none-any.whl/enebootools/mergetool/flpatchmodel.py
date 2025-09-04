# encoding: UTF-8
"""
    Módulo de cálculo y aplicación de parches PY_model emulando flpatch.
"""
"""
    -----
    Hay que anotar de algún modo cuando parcheamos una clase, qué clase 
    estábamos buscando. Esto servirá para que la próxima clase que busque esa
    misma, en su lugar herede de la nuestra y así preservar el correcto orden
    de aplicación.
    
    Ejemplo:
    
    class jasper extends num_serie /** %from: oficial */ {
    
    
    Aunque pueda parecer información excesiva, es normal, porque genera un 
    arbol 1->N y da la información exacta de la extensión/mezcla al usuario
    final.
    
"""

import re, os.path, difflib, math, itertools, shutil, sys, io
import pprint, subprocess

pp = pprint.PrettyPrinter(indent=4)


def latin1_to_ascii(unicrap):
    """This replaces UNICODE Latin-1 characters with
    something equivalent in 7-bit ASCII. All characters in the standard
    7-bit ASCII range are preserved. In the 8th bit range all the Latin-1
    accented letters are stripped of their accents. Most symbol characters
    are converted to something meaningful. Anything not converted is deleted.
    """
    xlate = {
        0xC0: "A",
        0xC1: "A",
        0xC2: "A",
        0xC3: "A",
        0xC4: "A",
        0xC5: "A",
        0xC6: "Ae",
        0xC7: "C",
        0xC8: "E",
        0xC9: "E",
        0xCA: "E",
        0xCB: "E",
        0xCC: "I",
        0xCD: "I",
        0xCE: "I",
        0xCF: "I",
        0xD0: "Th",
        0xD1: "N",
        0xD2: "O",
        0xD3: "O",
        0xD4: "O",
        0xD5: "O",
        0xD6: "O",
        0xD8: "O",
        0xD9: "U",
        0xDA: "U",
        0xDB: "U",
        0xDC: "U",
        0xDD: "Y",
        0xDE: "th",
        0xDF: "ss",
        0xE0: "a",
        0xE1: "a",
        0xE2: "a",
        0xE3: "a",
        0xE4: "a",
        0xE5: "a",
        0xE6: "ae",
        0xE7: "c",
        0xE8: "e",
        0xE9: "e",
        0xEA: "e",
        0xEB: "e",
        0xEC: "i",
        0xED: "i",
        0xEE: "i",
        0xEF: "i",
        0xF0: "th",
        0xF1: "n",
        0xF2: "o",
        0xF3: "o",
        0xF4: "o",
        0xF5: "o",
        0xF6: "o",
        0xF8: "o",
        0xF9: "u",
        0xFA: "u",
        0xFB: "u",
        0xFC: "u",
        0xFD: "y",
        0xFE: "th",
        0xFF: "y",
        0xA1: "!",
        0xA2: "{cent}",
        0xA3: "{pound}",
        0xA4: "{currency}",
        0xA5: "{yen}",
        0xA6: "|",
        0xA7: "{section}",
        0xA8: "{umlaut}",
        0xA9: "{C}",
        0xAA: "{^a}",
        0xAB: "<<",
        0xAC: "{not}",
        0xAD: "-",
        0xAE: "{R}",
        0xAF: "_",
        0xB0: "{degrees}",
        0xB1: "{+/-}",
        0xB2: "{^2}",
        0xB3: "{^3}",
        0xB4: "'",
        0xB5: "{micro}",
        0xB6: "{paragraph}",
        0xB7: "*",
        0xB8: "{cedilla}",
        0xB9: "{^1}",
        0xBA: "{^o}",
        0xBB: ">>",
        0xBC: "{1/4}",
        0xBD: "{1/2}",
        0xBE: "{3/4}",
        0xBF: "?",
        0xD7: "*",
        0xF7: "/",
    }

    r = ""
    for i in unicrap:
        if ord(i) in xlate:
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += i
    return r


def modelclass_reader(iface, file_name, file_lines):
    linelist = []
    classes = []
    delclasses = []
    declidx = {}
    defidx = {}
    iface_n = None
    classpatch = []
    for n, line in enumerate(file_lines):
        line2 = latin1_to_ascii(line)
        m = re.search(r"#\s*@\s*([\w\.,;-]+)\s+([^ #]+)", line2)
        if m:
            m2 = re.search(r"^\s*# @(\w+)( \w+)", line)
            if not m2:
                iface.warn("Formato incorrecto de la linea %s" % repr(line))
            dtype = m.group(1)
            cname = m.group(2)
            for n2, sline in enumerate(file_lines[n + 1 :]):
                sline2 = latin1_to_ascii(sline)
                sm = re.search(r"#\s*@\s*([\w\.,;-]+)\s+([^ #]+)", sline2)
                if sm:
                    break
            n2 += n + 1
            class_lines = file_lines[n:n2]
            heu_dtype = None
            heu_cname = None
            heu_extends = None
            # heu_from = None
            for l in class_lines[:32]:
                # m = re.search("class\s+(?P<cname>\w+)\(((?P<cbase>\w+),)?(((?P<cfrom>\w.)+))\)",l)
                m = re.search(
                    r"class\s+(?P<cname>([\w.])+)\(((?P<cbase>.+))(,(?P<cfrom>([\w.])+))?\)", l
                )
                if m:
                    heu_cname = m.group("cname")
                    heu_extends = m.group("cbase")
                    # heu_from = m.group("cfrom")
                    heu_dtype = "class_declaration"
            if heu_dtype is None:
                heu_cnames = []
                other_functions = []
                for l in class_lines:
                    m = re.search(r"def\s+(?P<cname>[a-zA-Z0-9]+)_\w+", l)
                    if m:
                        heu_cname = m.group("cname")
                        if heu_cname not in heu_cnames:
                            heu_cnames.append(heu_cname)
                        if heu_cname != cname:
                            other_functions.append(l)
                if len(heu_cnames) > 1:
                    iface.error(
                        "En la clase %s existen funciones para diferentes clases (file: %s)"
                        % (cname, file_name)
                    )
                    for l in other_functions:
                        iface.error(">>>" + l)

                    if cname in heu_cnames:
                        heu_cname = cname

                if heu_cname:
                    heu_dtype = "class_definition"

            if heu_dtype and dtype != "delete_class":
                heu_line = "# @%s %s #" % (heu_dtype, heu_cname)
                myline = "# @%s %s #" % (dtype, cname)
                if "_" in cname:
                    iface.info(
                        "La autodetección de contenido de bloques no funciona con clases que contengan el carácter de guión bajo como %r"
                        % cname
                    )
                elif heu_line != myline:
                    iface.error(
                        "La definición de bloque %r no corresponde con el contenido (file: %s:%d) ... asumiendo '%s'"
                        % (line2.strip(), file_name, n, heu_line)
                    )
                    dtype, cname = heu_dtype, heu_cname
                    classpatch += ["@@ -%d,1 +%d,1 @@" % (n + 1, n + 1)]
                    classpatch += ["-%s" % line2.rstrip()]
                    classpatch += ["+%s" % heu_line]

            npos = len(linelist)
            if dtype == "class_declaration":
                if cname in classes:
                    iface.error(
                        "Hay dos bloques 'class_declaration' para la clase %s (file: %s) ... asumiendo 'class_definiton'"
                        % (cname, file_name)
                    )
                    dtype = "class_definition"
                else:
                    classdecl = extract_class_decl_info(iface, class_lines)
                    if cname not in classdecl:
                        iface.error(
                            "Bloque 'class_declaration' con nombre erroneo clase %s no existe en el bloque (file: %s)"
                            % (cname, file_name)
                        )
                        possible_cnames = difflib.get_close_matches(cname, classdecl, 1)
                        if possible_cnames:
                            cname = possible_cnames[0]
                    classes.append(cname)
                    declidx[cname] = npos

            if dtype == "class_definition":
                if cname in defidx:
                    iface.error(
                        "Hay dos bloques 'class_definition' para la clase %s (file: %s)"
                        % (cname, file_name)
                    )
                else:
                    defidx[cname] = npos
                    if cname not in classes:
                        iface.error(
                            "Bloque 'class_definition' huérfano para la clase %s (file: %s)"
                            % (cname, file_name)
                        )
            elif dtype == "delete_class":
                # Clase a borrar cuando se aplique el parche.
                if cname in delclasses:
                    iface.error(
                        "Hay dos bloques 'delete_class' para la clase %s (file: %s)"
                        % (cname, file_name)
                    )
                else:
                    delclasses.append(cname)
            elif dtype == "file":
                # el tipo @file no lo gestionamos
                pass
            elif dtype == "class_declaration":
                pass
            else:
                iface.warn(
                    "Tipo de identificador doxygen no reconocido %s (file: %s)"
                    % (repr(dtype), file_name)
                )
                continue

            found = [dtype, cname, n]
            if len(linelist):
                linelist[-1].append(n)
            linelist.append(found)
        # const iface = new ifaceCtx( this );
        m = re.search(r"self.iface\s*=\s*(?P<classname>\w+)\(\s*self\s*\)", line)

        if m:
            iface_n = {
                "block": len(linelist) - 1,
                "classname": m.group("classname"),
                "line": n,
                "text": m.group(0),
            }
    if linelist:
        linelist[-1].append(len(file_lines))

    classlist = {
        "decl": declidx,
        "def": defidx,
        "classes": classes,
        "delclasses": delclasses,
        "list": linelist,
        "patch": classpatch,
        "iface": iface_n,
    }

    return classlist


def extract_class_decl_info(iface, text_lines):
    classdict = {}
    for n, line in enumerate(text_lines):
        m = re.search(r"class\s+(?P<cname>([\w.])+)\(((?P<cbase>.+))(,(?P<cfrom>([\w.])+))?\)", line)
        if m:
            cname = m.group("cname")
            classdict[cname] = {
                "name": cname,
                "extends": m.group("cbase"),
                # 'from': m.group("cfrom"),
                "text": m.group(0),
                "line": n,
            }

    return classdict


def file_reader(filename):
    try:
        f1 = open(filename, "r", encoding="UTF-8")
    except IOError:
        raise ValueError("File Not Found: %s" % repr(filename))
        return
    name = os.path.basename(filename)
    return name, [line.rstrip() for line in f1.readlines()]


def diff_model(iface, base, final):
    iface.debug("Procesando Diff PY_model $base:%s -> $final:%s" % (base, final))
    nbase, flbase = file_reader(base)
    nfinal, flfinal = file_reader(final)
    if flbase is None or flfinal is None:
        iface.info("Abortando Diff PY_model por error al abrir los ficheros")
        return
    clbase = modelclass_reader(iface, base, flbase)
    clfinal = modelclass_reader(iface, final, flfinal)
    created_classes_s = list(set(clfinal["classes"]) - set(clbase["classes"]))
    deleted_classes = list(set(clbase["classes"]) - set(clfinal["classes"]))
    # Mantener el orden en que se encontraron:
    created_classes = [clname for clname in clfinal["classes"] if clname in created_classes_s]

    if len(created_classes) == 0 and len(deleted_classes) == 0:
        iface.warn(
            "No se han detectado clases nuevas ni viejas. El parche quedará vacío. ($final:%s)"
            % (final)
        )
        return -1

    iface.debug2r(created=created_classes, deleted=deleted_classes)
    return extract_classes(iface, clfinal, flfinal, created_classes, deleted_classes)


def extract_classes_model(iface, final, classlist):
    if isinstance(classlist, str):
        classlist = classlist.split(",")
    iface.debug("Extrayendo clases PY_model $final:%s $classlist:%s" % (final, ",".join(classlist)))
    nfinal, flfinal = file_reader(final)
    if flfinal is None:
        iface.info("Abortando por error al abrir los ficheros")
        return
    clfinal = modelclass_reader(iface, final, flfinal)

    if len(classlist) == 0:
        iface.warn("No se han pasado clases. El parche quedará vacío. ($final:%s)" % (final))

    return extract_classes(iface, clfinal, flfinal, classlist)


def split_model_old(iface, final):
    iface.debug("Separando fichero PY_model %s . . . " % (final))
    nfinal, flfinal = file_reader(final)
    if flfinal is None:
        iface.info("Abortando por error al abrir los ficheros")
        return
    flfinal = [line.replace("\t", "        ") for line in flfinal]
    clfinal = modelclass_reader(iface, final, flfinal)
    nameroot, ext = os.path.splitext(final)
    dstfolder = nameroot + "-splitted"

    try:
        os.mkdir(dstfolder)
    except OSError:
        pass
    f1 = open(os.path.join(dstfolder, "index"), "w")
    f1.write("header\n")

    f2 = open(os.path.join(dstfolder, "header"), "w")
    stype, clname, line1, linen = clfinal["list"][0]
    f2.write("\n".join(flfinal[:line1]) + "\n")
    f2.close()
    parent_class = None
    for item in clfinal["list"]:
        stype, clname, line1, linen = item
        name = "%s-%s" % (str(stype).lower(), str(clname).lower())

        f1.write("%s\n" % name)
        f2 = open(os.path.join(dstfolder, name), "w")
        text = "\n".join(flfinal[line1:linen]) + "\n"
        if stype == "class_declaration" and parent_class:
            text = text.replace(parent_class, "{$parent_class}")

        f2.write(text)
        f2.close()
        parent_class = clname

    f1.write("tail\n")
    f2 = open(os.path.join(dstfolder, "tail"), "w")
    stype, clname, line1, linen = clfinal["list"][-1]
    f2.write("\n".join(flfinal[linen:]) + "\n")
    f2.close()


def split_model(iface, final, create_folder=True):
    iface.debug("Separando fichero PY_model %s . . . " % (final))
    nfinal, flfinal = file_reader(final)
    if flfinal is None:
        iface.info("Abortando por error al abrir los ficheros")
        return
    flfinal = [line.replace("\t", "        ") for line in flfinal]
    clfinal = modelclass_reader(iface, final, flfinal)
    cdfinal = extract_class_decl_info(iface, flfinal)
    nameroot, ext = os.path.splitext(final)
    if create_folder:
        dstfolder = nameroot + "-splitted"

        try:
            os.mkdir(dstfolder)
        except OSError:
            pass
    else:
        dstfolder = {}

    def opendst(name):
        if create_folder:
            f = open(os.path.join(dstfolder, name), "w")
        else:
            f = io.StringIO()
            dstfolder[name] = f
        return f

    if clfinal["iface"]:
        line = clfinal["iface"]["line"]
        flfinal[line] = ""

    f1 = opendst("patch_series")

    for n, classname in enumerate(clfinal["classes"]):
        if n > 0:
            fix_class(
                iface,
                flfinal,
                clfinal,
                cdfinal,
                classname,
                set_extends="PARENT_CLASS",
                set_from=None,
            )

        f1.write(classname + "\n")
        f2 = opendst(classname + ".py")
        if n == 0:
            stype, clname, line1, linen = clfinal["list"][0]
            f2.write("\n".join(flfinal[:line1]) + "\n")
            if stype not in ["decl", "def"]:
                f2.write("\n".join(flfinal[line1:linen]) + "\n")
        nblock1 = clfinal["decl"].get(classname)
        if nblock1:
            stype, clname, line1, linen = clfinal["list"][nblock1]
            f2.write("\n".join(flfinal[line1:linen]) + "\n")
        else:
            iface.warn("La clase %s no tiene bloque de declaracion" % classname)

        nblock2 = clfinal["def"].get(classname)
        if nblock2:
            stype, clname, line1, linen = clfinal["list"][nblock2]
            f2.write("\n".join(flfinal[line1:linen]) + "\n")

        if n == 0:
            stype, clname, line1, linen = clfinal["list"][-1]
            f2.write("\n".join(flfinal[linen:]) + "\n")

        # f2.close()

    # f1.close()
    return dstfolder


class PatchReader(object):
    def __init__(self, iface, folder, cname, parent_class, last_class):
        self.iface = iface
        self.last_class = last_class
        self.folder = folder
        self.cname = cname
        self.parent_class = parent_class
        if type(folder) is dict:
            self.name = folder.get("@name", "unknown")
            self.filename = cname + ".py"
            f1 = folder[self.filename]
            f1.seek(0)
            self.file = [line.rstrip() for line in f1.readlines()]
        else:
            self.filename = os.path.join(folder, cname + ".py")
            self.name, self.file = file_reader(self.filename)

        if self.file is None:
            iface.info("Abortando por error al abrir los ficheros")
            return
        self.classes = modelclass_reader(iface, self.filename, self.file)
        self.classdict = extract_class_decl_info(iface, self.file)
        if parent_class:
            fix_class(
                iface, self.file, self.classes, self.classdict, cname, set_extends=parent_class
            )
        if self.classes["iface"]:
            line = self.classes["iface"]["line"]
            self.file[line] = ""
            # fix_iface(self.iface, self.file, self.classes, self.last_class)

    def write_head(self, f2):
        stype, clname, line1, linen = self.classes["list"][0]
        f2.write("\n".join(self.file[:line1]) + "\n")
        if stype == "file":
            f2.write("\n".join(self.file[line1:linen]) + "\n")

    def write_tail(self, f2):
        stype, clname, line1, linen = self.classes["list"][-1]
        f2.write("\n".join(self.file[linen:]) + "\n")

    def write_decl(self, f2):
        for classname, nblock1 in list(self.classes["decl"].items()):
            stype, clname, line1, linen = self.classes["list"][nblock1]
            f2.write("\n".join(self.file[line1:linen]) + "\n")

    def write_def(self, f2):
        for classname, nblock1 in list(self.classes["def"].items()):
            stype, clname, line1, linen = self.classes["list"][nblock1]
            f2.write("\n".join(self.file[line1:linen]) + "\n")


def join_model(iface, dstfolder):
    if type(dstfolder) is dict:
        f1 = iface.output
        foldername = filename = dstfolder.get("@name", "unknown")
    else:
        head, foldername = os.path.split(dstfolder)
        filename = foldername.replace("-splitted", ".joined") + ".py"
        filepath = os.path.join(head, filename)
        iface.debug("Uniendo carpeta %s . . . " % (dstfolder))
        f1 = open(filepath, "w")

    def openr(folder, filename):
        if type(folder) is dict:
            f = folder[filename]
            f.seek(0)
        else:
            f = open(os.path.join(folder, filename))
        return f

    f1r = openr(dstfolder, "patch_series")
    classlist = [cname.strip() for cname in f1r if len(cname.strip())]
    if not classlist:
        iface.error("Lista de clases disponibles para unir vacía (operación abortada)")
        iface.error("Contenido fichero: %r" % openr(dstfolder, "patch_series").read())
        return
    f1r.close()

    patch = {}
    parent_class = None
    # p_iface = None
    for cname in classlist:
        patch[cname] = PatchReader(iface, dstfolder, cname, parent_class, classlist[-1])
        parent_class = cname

    p0 = patch[classlist[0]]
    p0.write_head(f1)

    for cname in classlist:
        p = patch[cname]
        p.write_decl(f1)

    f1.write("class FormInternalObj(qsatype.FormDBWidget):\n\n")
    f1.write("    def _class_init(self):\n\n")
    f1.write("        # DEBUG:: Const Declaration:\n\n")
    f1.write("        self.iface = %s(self)\n\n" % classlist[-1])

    for cname in classlist:
        p = patch[cname]
        p.write_def(f1)

    p0.write_tail(f1)
    # f1.close()
    iface.info("El fichero %s ha sido escrito correctamente." % (filename))


def patch_model_dir(iface, base, patch):
    iface.debug("Procesando Patch sobre carpeta model $base:%s + $patch:%s" % (base, patch))
    base_filename = base
    if os.path.isfile(base):
        base = split_model(iface, base, False)

    def openr(folder, filename):
        if type(folder) is dict:
            if filename not in folder:
                iface.error(
                    "Buscando fichero inexistente %s, candidatos %s"
                    % (filename, ", ".join(list(folder.keys())))
                )
                return None
            f = folder[filename]
            f.seek(0)
        else:
            f = open(os.path.join(folder, filename))
        return f

    f1 = open(patch)
    section = None
    subsection = None
    sections = {}
    seclist = []
    for line in f1:
        if line[-1] == "\n":
            line = line[:-1]
        code = line[:2]
        text = line[2:]
        if code == "@@":
            name = text.strip()
            nameidx = name.find(" ")
            if nameidx > 0:
                section, subsection = name[:nameidx], name[nameidx + 1 :]
            else:
                section = name
                subsection = None
            if section not in sections:
                sections[section] = {}
            if subsection not in sections[section]:
                sections[section][subsection] = []
            else:
                iface.error("Sección '@@%s' redeclarada" % name)
            seclist.append((section, subsection))
            continue
        if code == "..":
            section = None
            continue
        if section:
            sections[section][subsection].append((code, text))
    if type(base) is dict:
        destpath = {}
    else:
        destpath = base + "-patched"
        if os.path.isdir(destpath):
            shutil.rmtree(destpath)
        os.mkdir(destpath)

    def opendst(name):
        if type(destpath) is dict:
            f = io.StringIO()
            destpath[name] = f
        else:
            f = open(os.path.join(destpath, name), "w")
        return f

    patch_series = [cl.strip() for cl in openr(base, "patch_series") if cl.strip() != ""]
    patch_series_orig = patch_series[:]
    iface.debug2("Classes1: %s" % ",".join(patch_series))
    sec_rmcls = sections.get("remove-classes")
    if sec_rmcls:
        # iface.error("TODO: Remove Classes")
        for code, line in sec_rmcls[None]:
            if code == "- ":
                try:
                    patch_series.remove(line)
                except ValueError:
                    iface.info(
                        "La clase %s iba a ser eliminada del fichero, pero no la encontramos" % line
                    )

    iface.debug2("Classes2: %s" % ",".join(patch_series))
    sec_mvcls = sections.get("move-classes")
    if sec_mvcls:
        for code, line in sec_mvcls[None]:
            line = line.strip()
            if len(line) == 0:
                continue
            match = re.match(r"^([\w,]+) \((\w+)\) ([\w,]+)", line)
            if not match:
                iface.error("Línea de movimiento de clases malformada: %s" % (repr(line)))
                continue
            group1, relation, group2 = match.groups()
            if relation not in ["before"]:
                iface.error("Línea de movimiento con relación desconocida: %s" % (repr(relation)))
                continue
            group1 = group1.split(",")
            group2 = group2.split(",")
            cl_from = "???"
            for cl in group1:
                try:
                    idx = patch_series.index(cl)
                except ValueError:
                    iface.warn(
                        "La clase %s iba a ser movida antes de %s pero la primera no existe"
                        % (cl, cl_from)
                    )
                    continue

                for cl_from in group2:
                    try:
                        idx_from = patch_series.index(cl_from)
                    except ValueError:
                        iface.warn(
                            "La clase %s iba a ser movida antes de %s pero la segunda no existe"
                            % (cl, cl_from)
                        )
                        continue

                    if relation == "before":
                        if idx > idx_from:
                            patch_series[:] = (
                                patch_series[:idx_from]
                                + [patch_series[idx]]
                                + patch_series[idx_from:idx]
                                + patch_series[idx + 1 :]
                            )
                            idx = patch_series.index(cl)

            # print code, ":", line

    iface.debug2("Classes3: %s" % ",".join(patch_series))

    sec_addcls = sections.get("add-classes")
    if sec_addcls:
        # Este algoritmo no inserta las clases donde "simplemente deberían", sino
        # que asume que el fichero parcheado no tiene nada que ver con el parche
        # y aparecen en cualquier odren, no en el esperado.
        # Por tanto, lo que intentamos es ubicarlas en el mejor lugar posible.
        known_cls = []

        def add_known(code, line):
            if known_cls:
                lcode = known_cls[-1][0]
            else:
                lcode = None
            if lcode != code:
                known_cls.append([code, [], None, None])
            known_cls[-1][1].append(line)

        # Agrupar las clases en bloques según si son conocidas o a agregar
        for code, line in sec_addcls[None]:
            line = line.strip()
            if line == "":
                continue
            if code == "  ":
                if line in patch_series:
                    add_known(code, line)
            if code == "+ ":
                if line in patch_series:
                    iface.warn("TODO: Add Classes -  Clase %s ya existía" % line)
                    continue

                add_known(code, line)
        # Computar las posiciones de los bloques conocidos:
        for block in known_cls:
            code, linelist, minidx, maxidx = block
            if code == "  ":
                idxlist = [patch_series.index(cl) for cl in linelist]
                minidx = min(idxlist)
                maxidx = max(idxlist)
                block[2] = minidx
                block[3] = maxidx
        # Para los bloques nuevos, heredar de la información de los conocidos:
        for i, block in enumerate(known_cls):
            code, linelist, minidx, maxidx = block
            if code == "+ ":
                prev_max = [-0.5] + [
                    known_cls[k][3] + 0.5 for k in range(i) if known_cls[k][0] == "  "
                ]
                next_min = [
                    known_cls[k][2] - 0.5
                    for k in range(i + 1, len(known_cls))
                    if known_cls[k][0] == "  "
                ] + [len(patch_series) - 0.5]
                block[2] = max(prev_max)
                block[3] = min(next_min)

        # Procedemos a la inserción . . .
        last_idx = None
        new_patch_series = []
        for i, block in enumerate(known_cls):
            code, linelist, minidx, maxidx = block
            if code != "+ ":
                continue
            if minidx > maxidx:
                iface.error(
                    "Conflicto al colocar la(s) clase(s) %s entre %.1f-%.1f"
                    % (",".join(linelist), maxidx + 0.5, minidx - 0.5)
                )
                cllist = patch_series[int(maxidx + 0.5) : int(minidx + 0.5)]
                prev_classes = list(
                    itertools.chain(
                        *[linelist1 for code1, linelist1, a1, a2 in known_cls[:i] if code1 == "  "]
                    )
                )
                next_classes = list(
                    itertools.chain(
                        *[
                            linelist1
                            for code1, linelist1, a1, a2 in known_cls[i + 1 :]
                            if code1 == "  "
                        ]
                    )
                )
                cllist2 = []
                for cl in cllist:
                    if cl in prev_classes:
                        t = "<<"
                    elif cl in next_classes:
                        t = ">>"
                    else:
                        t = "--"
                    cllist2.append(t)
                errors = []
                for i in range(len(cllist2) + 1):
                    leftside = cllist2[:i]
                    rightside = cllist2[i:]
                    invalid = leftside.count(">>") + rightside.count("<<")
                    errors.append(invalid)
                idx = errors.index(min(errors))
                minidx = maxidx = maxidx + idx

            prev_idx = int(math.floor((minidx + maxidx) / 2.0))
            next_idx = prev_idx + 1
            new_patch_series += patch_series[last_idx:next_idx] + linelist
            last_idx = max([next_idx, last_idx])

        new_patch_series += patch_series[last_idx:]
        patch_series[:] = new_patch_series

    files_to_add = []
    iface.debug("Classes4: %s" % ",".join(patch_series))

    fw1 = opendst("patch_series")
    iface.debug("Escribiendo patch_series . . .")
    for cl in patch_series:
        fw1.write("%s\n" % cl)
        filename = "%s.py" % cl
        if type(base) is dict:
            if filename in base:
                destpath[filename] = base[filename]
            else:
                files_to_add.append(cl)
        else:
            src = os.path.join(base, filename)
            dst = os.path.join(destpath, filename)
            if os.path.isfile(src):
                shutil.copy(src, dst)
            else:
                files_to_add.append(cl)
    fw1.write("\n")
    # fw1.close()

    sec_patchcls = sections.get("patch-class")
    if sec_patchcls:
        for cls, list1 in list(sec_patchcls.items()):
            if cls not in patch_series:
                iface.warn("No se parchea clase inexistente %s" % cls)
                continue
            filename = "%s.py" % cls
            iface.debug("Parcheando %s. . ." % filename)
            orig = list(openr(base, filename))
            patched = patch_class_advanced(orig, list1, filename)
            fw1 = opendst(filename)
            for line in patched:
                fw1.write(line)
                fw1.write("\n")

    sec_addedcls = sections.get("added-class")
    if sec_addedcls:
        for cls, list1 in list(sec_addedcls.items()):
            filename = "%s.py" % cls
            iface.debug("Creando %s. . ." % filename)
            fw1 = opendst(filename)
            for code, line in list1:
                fw1.write(line)
                fw1.write("\n")

    if type(destpath) is dict:
        # Si estamos trabajando en memoria, imprimir el resultado:
        destpath["@name"] = base_filename
        join_model(iface, destpath)

    return True


def unicode2(t):
    if type(t) is str:
        return t
    if type(t) is not str:
        t = str(t)
    return t.decode("UTF-8", "replace")


def patch_class_advanced(orig, patch, filename="unknown"):
    # 1.. separar el parche en "hunks" (bloques)
    blocks = []
    block = []
    print(filename)
    for n, (code, line) in enumerate(patch):
        if code == "==":
            if block:
                blocks.append(block)
                block = []
        else:
            block.append((code, line))
    if block:
        blocks.append(block)

    orig_ = [line.rstrip() for line in orig]

    for num_block, block in enumerate(blocks):
        orig1 = [re.sub("[^A-Za-z]", "", line).strip() for line in orig_]
        # 2.. Para cada bloque...
        # 2.1.. primero hallar el bloque original:
        orig_block = [line for code, line in block if code in ("  ", "- ")]

        # 2.2.. hallar bloque A - nuevo
        new_block = [line.rstrip() for code, line in block if code in ("  ", "+ ")]
        # numbered_block = []
        # n = -1
        # name = "A"
        # for code, line in block:
        #    if code in ('  ', '- '):
        #        n+=1
        #        sn = 0
        #    else:
        #        sn += 1
        #    numbered_block.append( (n,code,name,sn, line) )

        # print " block: %d patch lines, of %d lines original code" % (len(block), len(orig_block))
        # 2.2.. comparar el bloque original con el fichero original, para encontrar la posición
        orig_block1 = [re.sub("[^A-Za-z]", "", line).strip() for line in orig_block]
        sm1 = difflib.SequenceMatcher()
        sm1.set_seqs(orig_block1, orig1)
        same_lines = []
        lenbtotal = 0
        for a, b, sz in sm1.get_matching_blocks():
            a_stream = "\n".join(orig_block1[a : a + sz])
            b_stream = "\n".join(orig1[b : b + sz])
            # print "A::", a_stream[:128]
            # print "B::", b_stream[:128]
            lena = len(re.sub("[^A-Za-z]", "", a_stream).strip())
            lenb = len(re.sub("[^A-Za-z]", "", b_stream).strip())
            lenbtotal += lenb
            if min([lena, lenb]) < 16:
                continue
            same_lines += list(range(b, b + sz))
        common_lines = len(same_lines)
        if common_lines == 0:
            continue
        minb = min(same_lines)
        maxb = max(same_lines) + 1
        relok = int(len(same_lines) * 100.0 / float(maxb - minb))
        print("RelOk:", relok, "lenlines:", len(same_lines), "lenbytes:", lenbtotal)
        c_block = orig_[minb - 1 : maxb]
        if relok < 30:
            print("Clin:", same_lines)
            print()
            print(" ::: BASE")
            print("\n".join(orig_block))
            print(" ::: REMOTE")
            print("\n".join(new_block))
            print(" ::: LOCAL")
            for n, line in enumerate(orig_):
                ch = " "
                if n < minb:
                    ch = "<"
                if n >= maxb:
                    ch = ">"

                print("%04d" % n, ch, line)
            print(" ----")

        # Reanalizar el parche::
        d = difflib.Differ()
        cmp0 = d.compare(orig_block, new_block)
        numbered_block = []
        n = -1
        name = "A"
        sn = 0
        for cdln in cmp0:
            code = cdln[0:2]
            line = cdln[2:]
            if code in ("  ", "- "):
                n += 1
                sn = 0
            else:
                sn += 1
            numbered_block.append((n, code, name, sn, line))

        # Análisis profundo
        d = difflib.Differ()
        cmp1 = d.compare(orig_block, orig_[minb:maxb])
        numbered_block2 = []
        n = -1
        name = "B"
        for cdln in cmp1:
            code = cdln[0:2]
            line = cdln[2:]
            if code in ("  ", "- "):
                n += 1
                sn = 0
            else:
                sn += 1
            numbered_block2.append((n, code, name, sn, line))
        a_diffs = [
            (n, code, name, line) for n, code, name, sn, line in numbered_block if code != "  "
        ]
        b_diffs = [
            (n, code, name, line) for n, code, name, sn, line in numbered_block2 if code != "  "
        ]
        if True:
            model_file = {}
            for n in sorted(numbered_block + numbered_block2):
                if n[1] not in ("  ", "- ", "+ "):
                    continue
                model_file[tuple(list(n)[:-1])] = n[-1]

            for x in list(model_file.keys()):
                n, code, name, sn = x
                altname = "A" if name == "B" else "B"
                if code == "- ":
                    try:
                        del model_file[(n, "  ", altname, sn)]
                    except KeyError:
                        pass
                    try:
                        if model_file[(n, "- ", altname, sn)] == model_file[(n, "- ", name, sn)]:
                            line = model_file[(n, "- ", altname, sn)]
                            model_file[(n, "- ", "C", sn)] = line
                            del model_file[(n, "- ", altname, sn)]
                            del model_file[(n, "- ", name, sn)]
                    except KeyError:
                        pass
                elif code == "  ":
                    try:
                        if model_file[(n, "  ", altname, sn)] == model_file[(n, "  ", name, sn)]:
                            line = model_file[(n, "  ", altname, sn)]
                            model_file[(n, "  ", "C", sn)] = line
                            del model_file[(n, "  ", altname, sn)]
                            del model_file[(n, "  ", name, sn)]
                    except KeyError:
                        pass

            def translate_keys(key):
                l = list(key[0])
                code = l[1]
                if code == "- ":
                    l[1] = "10"
                if code == "  ":
                    l[1] = "20"
                if code == "+ ":
                    l[1] = "30"
                return tuple(l)

            last_seen_a = -200
            last_seen_b = -200
            min_space = 100
            for k, line in sorted(list(model_file.items()), key=translate_keys):
                nline, code = k[0], k[2]
                if code == "A":
                    last_seen_a = nline
                if code == "B":
                    last_seen_b = nline
                if (
                    last_seen_a >= 0
                    and last_seen_b >= 0
                    and abs(last_seen_b - last_seen_a) < min_space
                ):
                    min_space = abs(last_seen_b - last_seen_a)

            if min_space < 6:
                basefile = "/tmp/%s.base.tmp" % filename
                remotefile = "/tmp/%s.base.tmp" % filename
                localfile = "/tmp/%s.base.tmp" % filename
                print(repr(basefile), repr(remotefile))
                open("/tmp/base.tmp", "w").write("\n".join(orig_block))
                open("/tmp/remote.tmp", "w").write("\n".join(new_block))
                open("/tmp/local.tmp", "w").write("\n".join(c_block))
                subprocess.check_output(
                    [
                        "kdiff3",
                        "/tmp/base.tmp",
                        "/tmp/remote.tmp",
                        "/tmp/local.tmp",
                        "-o",
                        "/tmp/merged.tmp",
                        "--auto",
                    ]
                )
                new_lines = [ln1.rstrip() for ln1 in open("/tmp/merged.tmp")]
                orig_[minb - 1 : maxb] = new_lines
                continue

            # if min_space < 5:
            #    print "<<<<< conflict %d" % min_space
            #    for k, line in sorted(model_file.items(), key=translate_keys):
            #        nlist = [ unicode2(k1) for k1 in k]
            #        ntext = u".".join(nlist)
            #        print ntext, unicode2(line)
            #    print ">>>>>"
            #    print

        base_pos = 0
        a_offset = 0
        b_offset = 0
        o_diffs = orig_block[:]

        new_block = []
        add_buffer_a = []
        add_buffer_b = []
        last_a_diff = 0
        last_b_diff = 0
        while True:
            if a_diffs and a_diffs[0][0] == base_pos:
                f_a_diff = a_diffs.pop(0)
                if f_a_diff[1] == "+ ":
                    a_offset += 1
                    add_buffer_a.append(f_a_diff[3])
                    last_a_diff = 0
                if f_a_diff[1] == "- ":
                    o_diffs[0] = None
                    last_a_diff = 0
                    if b_diffs and b_diffs[0][0] == base_pos and b_diffs[0][1] == "- ":
                        b_diffs.pop(0)
                        last_b_diff = 0
                continue

            if b_diffs and b_diffs[0][0] == base_pos:
                f_b_diff = b_diffs.pop(0)
                if f_b_diff[1] == "+ ":
                    b_offset += 1
                    add_buffer_b.append(f_b_diff[3])
                    last_b_diff = 0
                if f_b_diff[1] == "- ":
                    o_diffs[0] = None
                    last_b_diff = 0
                continue
            txt_a = "".join([x.strip() for x in add_buffer_a])
            txt_b = "".join([x.strip() for x in add_buffer_b])
            if txt_a == txt_b:
                add_buffer_b = []
            if o_diffs:
                f_o_diff = o_diffs.pop(0)
                # print f_o_diff
                if f_o_diff is not None:
                    new_block.append(f_o_diff)
                base_pos += 1
                last_a_diff += 1
                last_b_diff += 1

            if add_buffer_a:
                new_block += add_buffer_a
                add_buffer_a = []
            if add_buffer_b:
                new_block += add_buffer_b
                add_buffer_b = []

            if not o_diffs:
                break
        orig_[minb:maxb] = new_block

    return orig_


def diff_model_dir(iface, base, final):
    iface.debug("Procesando Diff de carpetas PY_model $base:%s -> $final:%s" % (base, final))

    iface.debug("Comparando clases en patch_series . . .")
    if os.path.isfile(base):
        base = split_model(iface, base, False)
    if os.path.isfile(final):
        final = split_model(iface, final, False)

    def openr(folder, filename):
        if type(folder) is dict:
            f = folder[filename]
            f.seek(0)
        else:
            f = open(os.path.join(folder, filename))
        return f

    f1 = openr(base, "patch_series")
    classlist1 = [cname.strip() for cname in f1 if len(cname.strip())]
    # f1.close()
    f1 = openr(final, "patch_series")
    classlist2 = [cname.strip() for cname in f1 if len(cname.strip())]
    # f1.close()
    classlist1a = classlist1[:]
    classlist2a = classlist2[:]

    clases_eliminadas = [c for c in classlist1 if c not in classlist2]
    clases_agregadas = [c for c in classlist2 if c not in classlist1]
    # El sentido de la operación debe ser:
    # 1.- Eliminar clases
    # 2.- Mover clases
    # 3.- Parchear clases
    # 4.- Agregar clases
    if clases_eliminadas:
        iface.debug("Clases eliminadas: " + ", ".join(clases_eliminadas))
        iface.output.write(b"@@remove-classes\n")
        for cls in classlist1:
            if cls in clases_eliminadas:
                code = "- "
            else:
                code = "  "
            iface.output.write(str("%s%s\n" % (code, cls)).encode("UTF-8"))
        iface.output.write(b"..\n")

    for c in clases_eliminadas:
        classlist1a.remove(c)
    for c in clases_agregadas:
        classlist2a.remove(c)

    assert len(classlist1a) == len(classlist2a)
    n1 = 0
    n2 = -1
    for n1, (a, b) in enumerate(zip(classlist1a, classlist2a)):
        if a != b:
            break
    for n2, (a, b) in reversed(list(enumerate(zip(classlist1a, classlist2a)))):
        if a != b:
            break
    # classlist1b y classlist2b mantienen el listado de clases discrepantes.
    classlist1b, classlist2b = classlist1a[n1 : n2 + 1], classlist2a[n1 : n2 + 1]
    classlist1b_n = [classlist2b.index(c) for c in classlist1b]

    move_actions = get_move_actions(classlist1b_n, classlist2b)
    if move_actions:
        iface.output.write(b"@@move-classes\n")
        for move_action in move_actions:
            iface.debug("Clases movidas: " + repr(move_action))
            cl2move, relation, clctx = move_action
            iface.output.write(
                str("  %s (%s) %s\n" % (",".join(cl2move), relation, ",".join(clctx))).encode(
                    "UTF-8"
                )
            )
        iface.output.write(b"..\n")

    if clases_agregadas:
        iface.debug("Clases agregadas: " + ", ".join(clases_agregadas))
        iface.output.write(b"@@add-classes\n")
        for cls in classlist2:
            if cls in clases_agregadas:
                code = "+ "
            else:
                code = "  "
            iface.output.write(str("%s%s\n" % (code, cls)).encode("UTF-8"))
        iface.output.write(b"..\n")

    clases_comunes = [c for c in classlist2 if c in classlist1]
    if iface.clean_patch:
        clases_comunes = []
        clases_agregadas = []

    for cls in clases_comunes:
        file1 = list(openr(base, cls + ".py"))
        file2 = list(openr(final, cls + ".py"))
        diff = list(difflib.ndiff(file1, file2))
        changed_lines = [
            (n, line)
            for n, line in enumerate(diff)
            if line[0:2] not in ["  "] and len(line[1:].rstrip()) > 1
        ]
        if changed_lines:
            iface.debug(" ##### FICHERO %s.py #####" % cls)
            iface.output.write(str("@@patch-class %s\n" % cls).encode("UTF-8"))
            unprinted_lines = list(range(len(diff)))
            for n, ld in changed_lines:
                if n not in unprinted_lines:
                    continue
                idx = unprinted_lines.index(n)
                prev_lines, post_lines = unprinted_lines[:idx], unprinted_lines[idx + 1 :]
                if len(prev_lines) > 3:
                    for j in reversed(prev_lines):
                        if re.search(r"^\s*(def|class) ", diff[j]):
                            break
                    omitted = len(prev_lines[: prev_lines.index(j)])
                    if omitted > 20:
                        omlines = prev_lines[: prev_lines.index(j)]
                        omlines_A = omlines[:10]
                        omlines_B = omlines[-10:]
                        for k in omlines_A:
                            iface.output.write(str(diff[k]).encode("UTF-8"))
                        iface.output.write(str("== %d lines ==\n" % (omitted - 20)).encode("UTF-8"))
                        for k in omlines_B:
                            iface.output.write(str(diff[k]).encode("UTF-8"))
                    else:
                        for k in prev_lines[: prev_lines.index(j)]:
                            iface.output.write(str(diff[k]).encode("UTF-8"))
                    for k in prev_lines[prev_lines.index(j) :]:
                        iface.output.write(str(diff[k]).encode("UTF-8"))
                else:
                    for k in prev_lines:
                        iface.output.write(str(diff[k]).encode("UTF-8"))
                unprinted_lines[: idx + 1] = []
                iface.output.write(str(diff[n]).encode("UTF-8"))

                post_lines = [x for x in unprinted_lines if x > n]
                end = False
                count = 0
                for b in post_lines:
                    if re.search("def", diff[b]):
                        end = True
                    if end and count > 1:
                        break

                    iface.output.write(str(diff[b]).encode("UTF-8"))
                    unprinted_lines.remove(b)
                    if diff[b][0:2] == "  ":
                        count += 1
                    else:
                        count = 0
                        end = False

            iface.output.write(b"..\n")
            iface.debug("-")

    for cls in clases_eliminadas:
        file1 = openr(base, cls + ".py")
        iface.output.write(str("@@removed-class %s\n" % cls).encode("UTF-8"))
        for line in file1:
            iface.output.write(str("  %s" % line).encode("UTF-8"))
        iface.output.write(b"..\n")

    for cls in clases_agregadas:
        file1 = openr(final, cls + ".py")
        iface.output.write(str("@@added-class %s\n" % cls).encode("UTF-8"))
        for line in file1:
            iface.output.write(str("  %s" % line).encode("UTF-8"))
        iface.output.write(b"..\n")

    iface.output.write(b"\n")
    return True


def get_move_actions(cln1, names):
    actions = []
    cln = cln1[:]
    for i in reversed(list(range(len(cln)))):
        if i == 0:
            break
        if cln[i - 1] < cln[i]:
            continue
        for j in reversed(list(range(-1, i))):
            if j < 0 or cln[j] < cln[i]:
                break

        beforen2 = cln[j + 1 : i]
        mbf2 = min(beforen2)
        for k in range(i, len(cln)):
            if k > mbf2:
                break
        beforen1 = cln[i : k + 1]

        actions.append(([names[i] for i in beforen1], "before", [names[i] for i in beforen2]))
        cln[i : k + 1] = []
        cln[j + 1 : i] = beforen1 + cln[j + 1 : i]

    return actions


def extract_classes(iface, clfinal, flfinal, classes2extract, classes2delete=[]):
    iface_line = -1
    if clfinal["iface"]:
        iface_line = clfinal["iface"]["line"]

    for clname in classes2delete:
        iface.output.write(b"\n")
        iface.output.write(str("/** @delete_class %s */" % clname).encode("UTF-8"))
        iface.output.write(b"\n")

    for clname in classes2extract:
        block_decl = clfinal["decl"].get(clname, None)
        if block_decl is None:
            iface.error("Se esperaba una declaración de clase para %s." % clname)
            continue
        dtype, clname, idx1, idx2 = clfinal["list"][block_decl]
        iface.debug2r(exported_block=clfinal["list"][block_decl])

        lines = flfinal[idx1:idx2]
        if iface_line >= idx1 and iface_line < idx2:
            # Excluir la definición "iface" del parche, en caso de que estuviese dentro
            rel_line = iface_line - idx1
            from_text = clfinal["iface"]["text"]
            assert lines[rel_line].find(from_text) != -1
            lines[rel_line] = lines[rel_line].replace(from_text, "")
        while lines[0].strip() == "":
            del lines[0]
        while lines[-1].strip() == "":
            del lines[-1]

        text = "\n".join(lines)
        iface.output.write(b"\n")
        iface.output.write(str(text).encode("UTF-8"))
        iface.output.write(b"\n")

    for clname in classes2extract:
        block_def = clfinal["def"].get(clname, None)
        if block_def is None:
            iface.debug("Se esperaba una definición de clase para %s." % clname)
            continue
        dtype, clname, idx1, idx2 = clfinal["list"][block_def]
        iface.debug2r(exported_block=clfinal["list"][block_def])
        lines = flfinal[idx1:idx2]
        while lines[0].strip() == "":
            del lines[0]
        while lines[-1].strip() == "":
            del lines[-1]

        text = "\n".join(lines)
        iface.output.write(b"\n")
        iface.output.write(str(text).encode("UTF-8"))
        iface.output.write(b"\n")

    iface.output.write(b"\n")
    return True


def check_model_classes(iface, base):
    iface.debug("Comprobando clases del fichero PY_model $filename:%s" % (base))
    nbase, flbase = file_reader(base)
    if flbase is None:
        iface.info("Abortando comprobación por error al abrir los ficheros")
        return
    clbase = modelclass_reader(iface, base, flbase)
    cpatch = clbase["patch"]
    if iface.patch_dest and cpatch:
        iface.info("Guardando parche en %r" % iface.patch_dest)
        fpatch = open(iface.patch_dest, "a")
        fpatch.write("--- a/" + base)
        fpatch.write("\n")
        fpatch.write("+++ b/" + base)
        fpatch.write("\n")
        fpatch.write("\n".join(cpatch))
        fpatch.write("\n")
        fpatch.close()

    classdict = extract_class_decl_info(iface, flbase)

    if not clbase["iface"]:
        iface.error("No encontramos declaración de iface.")
        return
    iface_clname = clbase["iface"]["classname"]
    iface.debug("Se encontró declaración iface de la clase %s" % (repr(iface_clname)))
    # Buscar clases duplicadas primero.
    # Los models no se ejecutaran bien si tienen clases duplicadas.
    for clname in set(clbase["classes"]):
        count = clbase["classes"].count(clname)
        if count > 1:
            iface.error("La clase %s se encontró %d veces" % (clname, count))
            return

    if iface_clname not in classdict:
        iface.error(
            "La declaración de iface requiere una clase %s" " que no existe." % (iface_clname)
        )
        return
    not_used_classes = clbase["classes"][:]
    iface_class_hierarchy = []
    current_class = iface_clname
    prev_class = "<no-class>"
    if clbase["iface"]["line"] < classdict[current_class]["line"]:
        iface.warn(
            "La declaración de iface requiere una clase %s"
            " que está definida más abajo en el código" % (current_class)
        )
    while True:
        if current_class not in not_used_classes:
            if current_class in clbase["classes"]:
                iface.error(
                    "La clase %s es parte de una "
                    "referencia circular (desde: %s)" % (current_class, prev_class)
                )
            else:
                iface.error(
                    "La clase %s no está " "definida (desde: %s)" % (current_class, prev_class)
                )
            return
        not_used_classes.remove(current_class)
        iface_class_hierarchy.insert(0, current_class)
        parent = classdict[current_class]["extends"]
        if parent is None:
            break

        if parent not in classdict or parent not in clbase["classes"]:
            iface.error(
                "La clase %s no está "
                "definida (extends de la clase %s, desde: %s)" % (parent, current_class, prev_class)
            )
            return

        if not check_class(iface, flbase, clbase, classdict, current_class):
            iface.error(
                "Se detectó algún problema en la clase %s"
                " (clase padre: %s, desde: %s)" % (current_class, parent, prev_class)
            )

        if classdict[current_class]["line"] < classdict[parent]["line"]:
            iface.error(
                "La clase %s hereda de una clase %s que está"
                " definida más abajo en el código" % (current_class, parent)
            )
            return
        current_class = parent

    # De las clases sobrantes, ninguna puede heredar de alguna que hayamos usado
    for clname in not_used_classes:
        try:
            parent = classdict[clname]["extends"]
        except KeyError:
            continue  # Este error generalmente se avisa antes
        if parent in iface_class_hierarchy:
            iface.error(
                "La clase %s no la heredó iface, y sin embargo,"
                " hereda de la clase %s que sí la heredó." % (clname, parent)
            )
            return
    iface.debug2r(classes=iface_class_hierarchy)
    iface.info2("La comprobación se completó sin errores.")
    return True


def patch_model(iface, base, patch):
    iface.debug("Procesando Patch PY_model $base:%s + $patch:%s" % (base, patch))
    nbase, flbase = file_reader(base)
    npatch, flpatch = file_reader(patch)
    if flbase is None or flpatch is None:
        iface.info("Abortando Patch PY_model por error al abrir los ficheros")
        return
    # classlist
    clpatch = modelclass_reader(iface, patch, flpatch)
    # classdict
    cdpatch = extract_class_decl_info(iface, flpatch)

    if clpatch["iface"]:
        iface.error("El parche contiene una definición de iface. No se puede aplicar.")
        return

    # iface.debug2r(clpatch=clpatch)
    # iface.debug2r(cdpatch=cdpatch)

    # Hallar el trabajo a realizar:
    #  - Hay que insertar en "base" las clases especificadas por clpatch['classes']
    #       en el mismo orden en el que aparecen.
    #  - Al insertar la clase agregamos en el extends un /** %from: clname */
    #       que indicará qué clase estábamos buscando.
    #  - Cuando insertemos una nueva clase, hay que ajustar las llamadas a la
    #       clase padre de la clase insertada y de la nueva clase hija
    #  - En caso de no haber nueva clase hija, entonces "iface" cambia de tipo.
    #       Además, probablemente haya que bajar la definición de iface.
    new_iface_class = None
    for newclass in clpatch["classes"] + clpatch["delclasses"]:
        auth_overwrite_class = False
        todo = []  # Diferentes "arreglos" que ejecutar luego.
        clbase = modelclass_reader(iface, base, flbase)
        cdbase = extract_class_decl_info(iface, flbase)
        if iface.patch_model_rewrite == "reverse":
            mode = "insert" if newclass in clpatch["delclasses"] else "delete"
        else:
            mode = "insert" if newclass in clpatch["classes"] else "delete"

        if mode == "delete":
            iface.debug("Procediendo a la *eliminación* de la clase %s" % newclass)
        else:
            iface.debug("Procediendo a la inserción de la clase %s" % newclass)

        if mode == "delete" and newclass not in clbase["classes"]:
            iface.info2(
                "La clase %s NO estaba insertada en el fichero, "
                "se OMITE el borrado de la clase." % newclass
            )
            continue

        # debería heredar de su extends, o su from (si existe).
        # si carece de extends es un error y se omite.
        if mode == "insert":
            extends = cdpatch[newclass]["extends"]
        else:
            extends = cdbase[newclass]["extends"]

        if mode == "delete":
            iface.info2(
                "La clase %s ya estaba insertada en el fichero, "
                "se procede a borrar la clase como se ha solicitado." % newclass
            )
            old_extends = cdbase[newclass]["extends"]
            for clname, cdict in list(cdbase.items()):
                # Si alguna clase extendía esta, ahora extenderá $old_extends
                if cdict["extends"] == newclass:
                    fix_class(iface, flbase, clbase, cdbase, clname, set_extends=old_extends)

            # TODO: Si iface era de tipo $newclass, ahora será de tipo $old_extends.

            remove_lines = []
            if newclass in clbase["decl"]:
                remove_lines.append(clbase["decl"][newclass])
                del clbase["decl"][newclass]

            if newclass in clbase["def"]:
                remove_lines.append(clbase["def"][newclass])
                del clbase["def"][newclass]

            for n in reversed(sorted(remove_lines)):
                del clbase["list"][n]

            clbase["classes"].remove(newclass)
            del cdbase[newclass]
        lower_classes = [str(x).lower() for x in clbase["classes"]]
        if str(newclass).lower() in lower_classes:
            if iface.patch_model_rewrite == "abort":
                iface.error(
                    "La clase %s ya estaba insertada en el fichero, "
                    "abortamos la operación." % newclass
                )
                return False
            if iface.patch_model_rewrite == "no":
                iface.warn(
                    "La clase %s ya estaba insertada en el fichero, "
                    "omitimos el parcheo de esta clase." % newclass
                )
                continue
            if iface.patch_model_rewrite == "yes":
                iface.info2(
                    "La clase %s ya estaba insertada en el fichero, "
                    "se sobreescribirá la clase." % newclass
                )

            if iface.patch_model_rewrite == "warn":
                iface.warn(
                    "La clase %s ya estaba insertada en el fichero, "
                    "se sobreescribirá la clase." % newclass
                )
            auth_overwrite_class = True
            idx = lower_classes.index(str(newclass).lower())
            oldclass = clbase["classes"][idx]
        if extends is None:
            iface.error(
                "La clase %s carece de extends y no es insertable como" " un parche." % newclass
            )
            continue

        # cfrom = cdpatch[newclass]['from']
        # if cfrom and cfrom != extends:
        #     iface.debug(u"class %s: Se ha especificado un %%from %s y "
        #                 u"tomará precedencia por encima del extends %s" % (
        #                 newclass, cfrom, extends) )
        #     extends = cfrom
        #     iface.debug(u"class %s: Se ha especificado un %%from %s, "
        #                u"pero se ignora y dejamos el extends %s" % (
        #                newclass, cfrom, extends) )

        extends = extends.split(", helpers.MixinConAcciones")[0]
        if extends not in clbase["classes"]:
            clsheur = 1  # <- cambiar modo de heuristica
            if clsheur == 1:
                try:
                    # Modo heuristico basico:
                    if newclass.startswith("pub"):
                        modelclass = "iface"
                    elif newclass.startswith("base"):
                        modelclass = "interna"
                    else:
                        modelclass = "oficial"
                    if modelclass not in clbase["classes"]:
                        modelclass = clbase["classes"][-1]

                    iface.warn(
                        "La clase %s debía heredar de %s, pero no "
                        "la encontramos en el fichero base. "
                        "En su lugar, heredará de %s." % (newclass, extends, modelclass)
                    )
                    extends = modelclass
                except IndexError:
                    iface.error(
                        "La clase %s debía heredar de %s, pero no "
                        "la encontramos en el fichero base." % (newclass, extends)
                    )
                    continue

            else:
                # Modo antiguo:
                iface.error(
                    "La clase %s debía heredar de %s, pero no "
                    "la encontramos en el fichero base." % (newclass, extends)
                )
                continue
        iface.debug("La clase %s deberá heredar de %s" % (newclass, extends))

        # Buscar la clase más inferior que heredó originalmente de "extends"
        if auth_overwrite_class:
            # extends = cdbase[oldclass]['from']
            extending = cdbase[oldclass]["extends"]
        else:
            extending = extends
            for classname in reversed(clbase["classes"]):
                # Buscamos del revés para encontrar el último.
                cdict = cdbase[classname]
                # if cdict['from'] == extends:
                #     extending = cdict['name']
                #     iface.debug(u"La clase %s es la última que heredó de %s, pasamos a heredar de ésta." % (extending,extends))
                #     break

        if mode == "insert":
            # Habrá que insertar el bloque entre dos bloques: parent_class y child_class.
            # Vamos a asumir que estos bloques están juntos y que child_class heredaba de parent_class.
            parent_class = clbase["decl"][extending]
            # Dónde guardar el código de definición: (después de la clase que extendimos)
            ext_class_idx = clbase["classes"].index(extending)
            if newclass in clpatch["def"]:
                while True:
                    ext_cname = clbase["classes"][ext_class_idx]
                    try:
                        child_def_block = clbase["def"][ext_cname] + 1
                        break
                    except KeyError:
                        ext_class_idx += 1
                        if ext_class_idx >= len(clbase["classes"]):
                            iface.info2(
                                "Se va a colocar el código de las "
                                "definiciones de la clase %s al"
                                " final del fichero." % (newclass)
                            )
                            child_def_block = max(clbase["def"].values()) + 1
                            break
            # else:
            #     child_def_block = max(clbase['def'].values()) + 1

            assert (
                clbase["list"][parent_class][1] == extending
            )  # <- este calculo deberia ser correcto.

            child_class = -1  # Supuestamente es el siguiente bloque de tipo "class_declaration".
            for n, litem in enumerate(clbase["list"][parent_class:]):
                if n == 0:
                    continue
                if litem[0] != "class_declaration":
                    continue
                child_class = parent_class + n
                break

            if child_class >= 0 and not auth_overwrite_class:
                prev_child_cname = clbase["list"][child_class][1]
                realExt = cdbase[prev_child_cname]["extends"]
                # $prev_child_name debería estar heredando de $extending.
                if realExt != extending:
                    if realExt == extending + ", helpers.MixinConAcciones":
                        # child_class = parent_class + 1
                        auth_overwrite_class = True
                    else:
                        iface.error(
                            "Se esperaba que la clase %s heredara de "
                            "%s, pero en cambio hereda de %s"
                            % (prev_child_cname, extending, cdbase[prev_child_cname]["extends"])
                        )
                        continue
                else:
                    iface.debug(
                        "La clase %s hereda de %s, pasará a heredar %s"
                        % (prev_child_cname, extending, newclass)
                    )
                    todo.append("fix-class prev_child_cname")
            else:
                # Si no había clase posterior, entonces marcamos como posición
                # de inserción el próximo bloque.
                child_class = parent_class + 1

            # Si la clase que vamos a heredar es la que está en el iface, entonces
            #   en el iface habrá que cambiarlo por la nuestra.
            if clbase["iface"]:  # -> primero comprobar que tenemos iface.
                iface.debug2r(iface=clbase["iface"])
                if clbase["iface"]["classname"] == extending:
                    iface.debug(
                        "La clase que estamos extendiendo (%s) es el "
                        "tipo de dato usado por iface, por lo tanto actualizamos"
                        " el tipo de dato usado por iface a %s" % (extending, newclass)
                    )
                    todo.append("fix-iface newclass")
                    new_iface_class = newclass
            else:
                prev_child_cname = clbase["list"][child_class][1]
                realExt = cdbase[prev_child_cname]["extends"]
                if realExt == extending + ", helpers.MixinConAcciones":
                    todo.append("fix-class prev_child_cname")
                else:
                    iface.warn(
                        "No existe declaración de iface en el código (aplicando patch para clase %s)"
                        % newclass
                    )
                    todo.append("create-iface")

            # Si la clase del parche que estamos aplicando pasa a extender otra
            # clase con nombre distinto, actualizaremos también los constructores.
            if cdpatch[newclass]["extends"] != extending:
                iface.debug(
                    "La clase %s extendía %s en el parche, pasará a"
                    " heredar a la clase %s" % (newclass, cdpatch[newclass]["extends"], extending)
                )
                todo.append("fix-class newclass")

        # Bloques a insertar:
        newblocklist = clbase["list"][:]
        if mode == "insert":
            if newclass in clpatch["def"]:
                try:
                    from_def_block = clpatch["list"][clpatch["def"][newclass]]
                    # incrustamos en posicion $child_def_block
                    if newclass in clbase["classes"]:
                        # Sobreescribimos el bloque si ya existe la clase.
                        assert auth_overwrite_class
                        newblocklist[clbase["def"][newclass]] = from_def_block
                    else:
                        newblocklist.insert(child_def_block, from_def_block)

                    # Se hace en orden inverso (primero abajo, luego arriba) para evitar
                    # descuadres, por tanto asumimos:
                    assert child_def_block > child_class

                except KeyError:
                    iface.info2("La clase %s carece de bloque de definición." % newclass)

            from_decl_block = clpatch["list"][clpatch["decl"][newclass]]
            # incrustamos en posicion $child_class
            if newclass in clbase["classes"]:
                assert auth_overwrite_class
                newblocklist[clbase["decl"][newclass]] = from_decl_block
            else:
                newblocklist.insert(child_class, from_decl_block)

        newbase = []  # empezamos la creación del nuevo fichero

        # insertamos las líneas de cabecera (hasta el primer bloque)
        idx1 = clbase["list"][0][2]
        newbase += flbase[:idx1]

        # iteramos por la lista de bloques y vamos procesando.
        for btype, bname, idx1, idx2 in newblocklist:
            # ATENCION: Sabemos que un bloque viene del parche o de base porque
            # .. tiene la clase $newclass que no está en base. Si esta condición
            # .. no se cumple, entonces el algoritmo falla.
            if bname == newclass:
                source = "patch"
            else:
                source = "base"

            if source == "base":
                block = flbase[idx1:idx2]
            elif source == "patch":
                block = flpatch[idx1:idx2]
            else:
                raise AssertionError

            while block[0] == "":
                del block[0]
            while block[-1] == "":
                del block[-1]
            block.append("")
            newbase += block

        # Ya tenemos el fichero montado:
        flbase = newbase
        # Recalculamos:
        clbase = modelclass_reader(iface, base, flbase)
        cdbase = extract_class_decl_info(iface, flbase)

        # Procesar tareas (to-do)
        if mode == "insert":
            fix_class(
                iface, flbase, clbase, cdbase, newclass, set_extends=extending, set_from=extends
            )
            if "fix-class newclass" in todo:
                # Esta tarea se realiza en la linea anterior incondicionalmente.
                todo.remove("fix-class newclass")

            if "fix-class prev_child_cname" in todo:
                iface.debug2r(prev_child_cname)
                fix_class(iface, flbase, clbase, cdbase, prev_child_cname, set_extends=newclass)
                # Al terminar, borramos la tarea.
                todo.remove("fix-class prev_child_cname")

            if "fix-iface newclass" in todo:
                fix_iface(iface, flbase, clbase, new_iface_class)
                todo.remove("fix-iface newclass")

        for task in todo:
            iface.warn("La tarea %s no se ejecutó o se desconoce cómo hacerlo." % repr(task))

    line = ""
    for line in flbase:
        iface.output.write(line.encode("UTF-8"))
        iface.output.write("\n".encode("UTF-8"))

    if line:
        iface.output.write("\n".encode("UTF-8"))

    return True


def fix_iface(iface, flbase, clbase, newclass):
    oldclass = clbase["iface"]["classname"]
    oldtext = clbase["iface"]["text"]
    newtext = oldtext.replace(" %s(" % oldclass, " %s(" % newclass, 1)
    line = clbase["iface"]["line"]
    oldline = flbase[line]
    newline = oldline.replace(oldtext, newtext, 1)
    iface.debug("%d: %s -> %s" % (line, oldline, newline))
    flbase[line] = newline
    clbase["iface"]["text"] = newtext
    clbase["iface"]["classname"] = newclass


def fix_class(iface, flbase, clbase, cdbase, classname, **updates):
    """
    Busca en $base la clase $class_name y modifica el código según los
    cambios en $**updates.
    Updates puede contener los siguientes tipos de argumentos:

    set_extends = actualiza la herencia de la clase
    set_from = actualiza la sentencia from
    """
    # iface.debug2r(clbase=clbase)
    # iface.debug2r(cdbase=cdbase)
    dclassname = classname
    if dclassname not in cdbase:
        close_matches = difflib.get_close_matches(classname, list(cdbase.keys()), 1, 0.80)
        if close_matches:
            iface.warn(
                "La clase %s no existe y se eligió en su lugar %s"
                % (repr(dclassname), repr(close_matches[0]))
            )
            dclassname = close_matches[0]
        else:
            iface.error(
                "La clase %s no existe y no encontramos ninguna en su lugar. Se aborta fix_class!!!"
                % (dclassname)
            )
            return None

    set_extends = updates.get("set_extends", -1)
    set_from = updates.get("set_from", -1)
    if set_extends == -1 and set_from == -1:
        raise ValueError

    if set_extends != -1:
        extends = set_extends
    else:
        extends = cdbase[dclassname]["extends"]

    # if dclassname == clbase["classes"][-1:][0]:
    extends += ", helpers.MixinConAcciones"

    # if set_from != -1: cfrom = set_from
    # else: cfrom = cdbase[dclassname]['from']

    # Reescribir sentencia class:
    line_no = cdbase[dclassname]["line"]
    old_expr = cdbase[dclassname]["text"]
    new_expr = "class %s" % classname
    if extends:
        new_expr += "(%s)" % extends
    # if cfrom: new_expr += " /** %%from: %s */" % cfrom

    flbase[line_no] = flbase[line_no].replace(old_expr, new_expr)

    if cdbase[dclassname]["extends"] != extends:
        # Si se ha cambiado la herencia
        decl_block_no = clbase["decl"][classname]
        end_line = clbase["list"][decl_block_no][3]
        for n, line in enumerate(flbase[line_no:end_line], line_no):
            m_it = re.finditer(
                r"def\s*__init__\(self, context\s*=\s*None\):\n\s*super\(?P<fname>\w+,\s*self\)\.__init__\(\s*context\s*\)",
                line,
            )
            for m in m_it:
                if m.group("fname") != cdbase[dclassname]["extends"]:
                    continue
                old = m.group(0)
                new = str(m.group(0)).replace(cdbase[dclassname]["extends"], extends, 1)
                flbase[n] = line.replace(old, new, 1)
                # iface.debug2r(line = line)
                # iface.debug2r(new_line = flbase[n])

    cdbase[dclassname]["extends"] = extends
    # cdbase[dclassname]['from'] = cfrom


def check_class(iface, flbase, clbase, cdbase, classname):
    """
    Busca en $base la clase $class_name y comprueba que sea correcta.
    """

    extends = cdbase[classname]["extends"]

    line_no = cdbase[classname]["line"]
    old_expr = cdbase[classname]["text"]
    new_expr = "class %s" % classname

    decl_block_no = clbase["decl"][classname]
    end_line = clbase["list"][decl_block_no][3]
    found = []
    line_found = []
    for n, line in enumerate(flbase[line_no:end_line], line_no):
        # match = list(re.finditer("def\s*__init__\(self, context\s*=\s*None\):\n\s*super\(?P<fname>\w+,\s*self\)\.__init__\(\s*context\s*\)", line))
        match = list(
            re.finditer(r"super\((?P<fname>\w+),\s*self\)\.__init__\(\s*context\s*\)", line)
        )
        if match:
            line_found.append(line)
            found += match

    if len(line_found) < 1:
        iface.error("No encontramos lineas candidatas a constructor")
        return False
    if len(line_found) > 1:
        iface.error("Encontramos más de una linea candidata a constructor: %s" % repr(line_found))
        return False
    # for m in found:
    #     old = m.group(0)
    #     new = str(m.group(0)).replace(m.group(0),extends,1)
    #     if extends != m.group(0):
    #         iface.error("Leimos %s pero deberia ser %s (%s)" % (old,new,line_found[0]))
    #         return False

    return True


"""
    Análisis de reordenación de clases:

    Primero eliminamos toda clase en A y B que haya sido agregada o eliminada. 
    Dejamos solo las clases comunes a las dos versiones.

    Luego, se examina hacia abajo cuantas clases consecutivamente coinciden en 
    orden hasta que encontramos la primera que no coincide. Eliminamos todo el bloque
    superior de clases que coinciden. Hacemos lo mismo de abajo a arriba.

    Se realiza un análisis de movimientos mínimos para llegar del set A al set B.
    
    Para realizar este análisis, seguimos el algoritmo de ordenación por inserción:
    
    http://es.wikipedia.org/wiki/Ordenamiento_por_inserci%C3%B3n
    
    Según este sistema, asignamos un número a cada clase del 1 a la 99 según su 
    orden en B (destino).
    
    Luego, usando el algoritmo de ordenacion calculamos los movimientos mínimos
    para llegar de A a B.
    
    Se analiza siempre de del final hacia adelante, buscando cuando un número es
    menor que su anterior. Ese número se desplaza hacia la izquierda tantas veces
    hasta que su anterior sea menor o no haya más antes. 
    
    Por ejemplo, con la siguente secuencia, tendríamos:
    
    ::::   3412576
    ext 6 : 1 posicion a la izquierda

    ::::   3412567
    ext 1 : 2 posiciones a la izquierda

    ::::   1342567
    ext 2 : 2 posiciones a la izquierda

    ::::   1234567
    Ok.
    
    Esto guardará unas instrucciones a modo de parche:
    
    clase 6 antes de 7
    clase 1 antes de 3 y de 4
    clase 2 después de 1 (este "después" se agrega porque se está moviendo en medio de la anterior)
    

    
"""
