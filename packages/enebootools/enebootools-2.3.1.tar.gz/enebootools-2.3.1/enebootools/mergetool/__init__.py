# encoding: UTF-8
import enebootools
from enebootools import EnebooToolsInterface
import traceback


ONLY_FILES = []

from enebootools.mergetool import (
    flpatchqs,
    flpatchpy,
    flpatchtest,
    flpatchmodel,
    flpatchxml,
    flpatchlxml,
    flpatchdir,
    projectbuilder,
    flpatchapipy,
)

"""
    El receptor de las llamadas del parser es una clase. Cada opción
    activada, genera una llamada en una función de la clase y así va 
    configurando la clase con cada llamada consecutiva.
    
    Esta clase está a nivel de módulo (mergetool) y es la interfaz
    de conexión de un módulo a otro.
    
    Una opción --output-file generara una llamada a una función miembro 
    "self.set_output_file(value)", donde "value" sería el valor recibido por
    la opción. 
    
    En el caso de que la opción no lleve valor, se ejecuta la función sin 
    argumentos.
    
    Las opciones cortas se configuran unicamente como alias de opciones 
    largas, de ese modo aprovechamos la configuración de unas cosas para otras.
    Y además, forzamos a que toda opción corta tenga su correspondiente opción 
    larga.
    
    Las acciones serán ejecutadas al final, y se les pasará los parámetros
    indicados con kwargs, de modo que el orden de los parámetros en la función
    es irrelevante, pero deben contar con el mismo nombre. 

    Las listas de ficheros se inicializan en el primer paso recibiendo el 
    array de ficheros, probablemente con una llamada a set_file_list.

    La ejecución de las acciones es prearada en el parse() pero no se ejecutan
    hasta la llamada de una segunda funcion execute_actions() para evitar 
    sobrecargar la pila de llamadas (y que cuando se lance un traceback sea 
    lo más sencillo posible).
    
    NOTAS: 
     * Los parámetros pueden llegar a ser omisibles?
        en tal caso o se omiten los últimos o tiene que poder darles nombre 
        o tiene que haber un argumento de exclusión como "-".
        
     * Múltiples acciones realizadas por ejecución?
        Si los parámetros de la acción se consumen se podría entender que se 
        inicia otra acción o concatenar mediante un separador. Esto generaría 
        problemas y es posible que no sea práctico para ningún caso. Es 
        posible reciclar opciones y parámetros de llamada entre acciones?
        ... de momento se provee de una interfaz interna para esto, pero no se
        va a usar.
    
     * Habrá que agregar un control de excepciones en las llamadas de cada 
        función, para intentar buscar errores en la propia llamada (funcion no 
        existe, argumentos no válidos... etc)
    
"""


class MergeToolInterface(EnebooToolsInterface):
    module_description = "Herramientas para la ayuda de resolución de conflictos de mezcla"

    def __init__(self, setup_parser=True):
        EnebooToolsInterface.__init__(self, False)
        self.patch_qs_rewrite = "warn"
        self.patch_py_rewrite = "warn"
        self.patch_test_rewrite = "warn"
        self.patch_model_rewrite = "warn"
        self.patch_xml_style_name = "legacy1"
        self.patch_qs_style_name = "legacy"
        self.patch_py_style_name = "legacy"
        self.patch_test_style_name = "legacy"
        self.patch_model_style_name = "legacy"
        self.diff_xml_search_move = False
        self.patch_name = None
        self.patch_dest = None
        self.clean_patch = False
        if setup_parser:
            self.setup_parser()

    def setup_parser(self):
        EnebooToolsInterface.setup_parser(self)
        self.parser.declare_option(
            name="patch-qs-rewrite",
            description="indica si al aplicar un parche de QS se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_qs_rewrite,
        )
        self.parser.declare_option(
            name="patch-py-rewrite",
            description="indica si al aplicar un parche de PY se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_py_rewrite,
        )
        self.parser.declare_option(
            name="patch-test-rewrite",
            description="indica si al aplicar un parche de PY_test se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_test_rewrite,
        )
        self.parser.declare_option(
            name="patch-model-rewrite",
            description="indica si al aplicar un parche de PY_model se debe sobreescribir o no las clases existentes ( reverse / predelete / yes / warn / no / abort ) ",
            level="action",
            variable="VALUE",
            call_function=self.set_patch_model_rewrite,
        )
        self.parser.declare_option(
            name="patch-name",
            description="Indica el nombre del parche que se usará en lugar de autodetectarlo.",
            level="action",
            variable="NAME",
            call_function=self.set_patch_name,
        )
        self.parser.declare_option(
            name="patch-dest",
            description="Donde guardar un fichero de parche",
            level="action",
            variable="FILENAME",
            call_function=self.set_patch_dest,
        )
        self.parser.declare_option(
            name="enable-diff-xml-search-move",
            description="Activa la búsqueda de movimientos de bloques XML. Puede ser un poco más lento y puede generar parches incompatibles con otras herramientas.",
            level="action",
            call_function=self.enable_diff_xml_search_move,
        )
        self.parser.declare_option(
            name="patch-xml-style",
            description="Usar otro estilo para generar parches XML (ver mergetools/etc/patch-styles/)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_xml_style,
        )
        self.parser.declare_option(
            name="patch-qs-style",
            description="Usar otro estilo para generar parches QS (legacy|qsdir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_qs_style,
        )
        self.parser.declare_option(
            name="patch-py-style",
            description="Usar otro estilo para generar parches PY (legacy|pydir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_py_style,
        )
        self.parser.declare_option(
            name="patch-test-style",
            description="Usar otro estilo para generar parches PY_test (legacy|testdir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_test_style,
        )
        self.parser.declare_option(
            name="patch-model-style",
            description="Usar otro estilo para generar parches PY_model (legacy|modeldir)",
            variable="NAME",
            level="action",
            call_function=self.set_patch_model_style,
        )
        self.parser.declare_option(
            name="clean-patch",
            description="provoca que el parche generado sea de tipo limpieza",
            level="action",  # ( action | parser )
            variable=None,
            call_function=self.set_clean_patch,
        )

        self.build_project_action = self.parser.declare_action(
            name="build-project",
            args=["buildxml"],
            options=[],
            description="Lee el fichero $buildxml y realiza las operaciones que se determinan",
            call_function=self.do_build_project,
        )
        self.build_project_action.set_help_arg(
            buildxml="Fichero del que leer las instrucciones",
        )

        self.folder_diff_action = self.parser.declare_action(
            name="folder-diff",
            args=["patchdir", "basedir", "finaldir"],
            options=["patch-name", "patch-qs-style", "patch-xml-style"],
            description="Genera en $patchdir una colección de parches de la diferencia entre las carpetas $basedir y $finaldir",
            call_function=self.do_folder_diff,
        )

        self.folder_diff_action = self.parser.declare_action(
            name="folder-diff",
            args=["patchdir", "basedir", "finaldir"],
            options=["patch-name", "patch-py-style", "patch-test-style", "patch-xml-style"],
            description="Genera en $patchdir una colección de parches de la diferencia entre las carpetas $basedir y $finaldir",
            call_function=self.do_folder_diff,
        )

        self.folder_diff_action = self.parser.declare_action(
            name="folder-diff",
            args=["patchdir", "basedir", "finaldir"],
            options=["patch-name", "patch-py-style", "patch-model-style", "patch-xml-style"],
            description="Genera en $patchdir una colección de parches de la diferencia entre las carpetas $basedir y $finaldir",
            call_function=self.do_folder_diff,
        )
        self.folder_diff_action.set_help_arg(
            patchdir="Carpeta donde guardar las diferencias",
            basedir="Carpeta a leer como referencia",
            finaldir="Carpeta a comparar",
        )

        self.folder_patch_action = self.parser.declare_action(
            name="folder-patch",
            args=["patchdir", "basedir", "finaldir"],
            options=["patch-name"],
            description="Aplica los parches en $patchdir a la carpeta $basedir y genera $finaldir",
            call_function=self.do_folder_patch,
        )
        self.folder_patch_action.set_help_arg(
            patchdir="Carpeta donde leer las diferencias",
            basedir="Carpeta a leer como referencia",
            finaldir="Carpeta a aplicar los cambios",
        )

        self.file_diff_action = self.parser.declare_action(
            name="file-diff",
            args=["ext", "base", "final"],
            description="Genera un parche de fichero $ext de la diferencia entre el fichero $base y $final",
            options=["output-file", "clean-patch"],
            call_function=self.do_file_diff,
            min_file_list=0,  # por defecto es 0
            max_file_list=0,  # por defecto es 0, -1 indica sin límite.
            min_argcount=-1,  # cantidad de argumentos obligatorios. por defecto -1
        )
        self.file_diff_action.set_help_arg(
            ext="Tipo de fichero a procesar: QS / XML / PY / PY_test",
            base="Fichero original",
            final="Fichero final",
        )
        self.file_patch_action = self.parser.declare_action(
            name="file-patch",
            args=["ext", "base", "patch"],
            description="Aplica un parche de fichero $ext especificado por $patch al fichero $base",
            options=[
                "output-file",
                "patch-qs-rewrite",
                "patch-py-rewrite",
                "patch-test-rewrite",
                "enable-diff-xml-search-move",
                "patch-xml-style",
            ],
            call_function=self.do_file_patch,
        )
        self.file_patch_action.set_help_arg(
            ext="Tipo de fichero a procesar: QS / XML / PY / PY_test",
            base="Fichero original",
            patch="Parche a aplicar sobre $base",
        )
        self.file_diff_action.set_help_arg(
            ext="Tipo de fichero a procesar: QS / XML / PY / PY_model",
            base="Fichero original",
            final="Fichero final",
        )
        self.file_patch_action = self.parser.declare_action(
            name="file-patch",
            args=["ext", "base", "patch"],
            description="Aplica un parche de fichero $ext especificado por $patch al fichero $base",
            options=[
                "output-file",
                "patch-qs-rewrite",
                "patch-py-rewrite",
                "patch-model-rewrite",
                "enable-diff-xml-search-move",
                "patch-xml-style",
            ],
            call_function=self.do_file_patch,
        )
        self.file_patch_action.set_help_arg(
            ext="Tipo de fichero a procesar: QS / XML / PY / PY_model",
            base="Fichero original",
            patch="Parche a aplicar sobre $base",
        )
        self.file_check_action = self.parser.declare_action(
            name="file-check",
            args=["check", "filename"],
            description="Analiza un fichero $filename en busca de errores usando el algoritmo de comprobación $check",
            options=["patch-dest"],
            call_function=self.do_file_check,
        )
        self.file_check_action.set_help_arg(
            check="Tipo de análisis a realizar: qs-classes / ...",
            filename="Fichero a analizar",
        )
        self.qs_extract_action = self.parser.declare_action(
            name="qs-extract",
            args=["final", "classlist"],
            description="Extrae del fichero $final las clases indicadas en $classlist",
            options=["output-file"],
            call_function=self.do_qs_extract,
        )
        self.py_extract_action = self.parser.declare_action(
            name="py-extract",
            args=["final", "classlist"],
            description="Extrae del fichero $final las clases indicadas en $classlist",
            options=["output-file"],
            call_function=self.do_py_extract,
        )
        self.test_extract_action = self.parser.declare_action(
            name="test-extract",
            args=["final", "classlist"],
            description="Extrae del fichero $final las clases indicadas en $classlist",
            options=["output-file"],
            call_function=self.do_test_extract,
        )
        self.model_extract_action = self.parser.declare_action(
            name="model-extract",
            args=["final", "classlist"],
            description="Extrae del fichero $final las clases indicadas en $classlist",
            options=["output-file"],
            call_function=self.do_model_extract,
        )
        self.qs_extract_action.set_help_arg(
            final="Fichero QS que contiene las clases a extraer",
            classlist="Lista de clases a extraer, separadas por coma y sin espacios: class1,class2,...",
        )
        self.py_extract_action.set_help_arg(
            final="Fichero PY que contiene las clases a extraer",
            classlist="Lista de clases a extraer, separadas por coma y sin espacios: class1,class2,...",
        )
        self.test_extract_action.set_help_arg(
            final="Fichero PY_test que contiene las clases a extraer",
            classlist="Lista de clases a extraer, separadas por coma y sin espacios: class1,class2,...",
        )
        self.model_extract_action.set_help_arg(
            final="Fichero PY_model que contiene las clases a extraer",
            classlist="Lista de clases a extraer, separadas por coma y sin espacios: class1,class2,...",
        )

        self.qs_split_action = self.parser.declare_action(
            name="qs-split",
            args=["final"],
            description="Separa el fichero $final en subficheros en una carpeta",
            options=[],
            call_function=self.do_qs_split,
        )
        self.qs_split_action.set_help_arg(
            final="Fichero QS",
        )

        self.qs_join_action = self.parser.declare_action(
            name="qs-join",
            args=["folder"],
            description="Une la carpeta $folder en un fichero",
            options=[],
            call_function=self.do_qs_join,
        )
        self.qs_join_action.set_help_arg(
            folder="Carpeta con los subficheros QS",
        )

        self.py_split_action = self.parser.declare_action(
            name="py-split",
            args=["final"],
            description="Separa el fichero $final en subficheros en una carpeta",
            options=[],
            call_function=self.do_py_split,
        )
        self.py_split_action.set_help_arg(
            final="Fichero PY",
        )
        self.test_split_action = self.parser.declare_action(
            name="test-split",
            args=["final"],
            description="Separa el fichero $final en subficheros en una carpeta",
            options=[],
            call_function=self.do_test_split,
        )
        self.test_split_action.set_help_arg(
            final="Fichero PY_test",
        )
        self.model_split_action = self.parser.declare_action(
            name="model-split",
            args=["final"],
            description="Separa el fichero $final en subficheros en una carpeta",
            options=[],
            call_function=self.do_model_split,
        )
        self.model_split_action.set_help_arg(
            final="Fichero PY_model",
        )

        self.py_join_action = self.parser.declare_action(
            name="py-join",
            args=["folder"],
            description="Une la carpeta $folder en un fichero",
            options=[],
            call_function=self.do_py_join,
        )
        self.py_join_action.set_help_arg(
            folder="Carpeta con los subficheros PY",
        )
        self.test_join_action = self.parser.declare_action(
            name="test-join",
            args=["folder"],
            description="Une la carpeta $folder en un fichero",
            options=[],
            call_function=self.do_test_join,
        )
        self.test_join_action.set_help_arg(
            folder="Carpeta con los subficheros PY_test",
        )
        self.model_join_action = self.parser.declare_action(
            name="model-join",
            args=["folder"],
            description="Une la carpeta $folder en un fichero",
            options=[],
            call_function=self.do_model_join,
        )
        self.model_join_action.set_help_arg(
            folder="Carpeta con los subficheros PY_model",
        )

    def set_patch_name(self, name):
        if name == "":
            name = None
        self.patch_name = name

    def set_patch_dest(self, filename):
        if filename == "":
            filename = None
        self.patch_dest = filename

    def set_patch_xml_style(self, name):
        self.patch_xml_style_name = name

    def set_patch_qs_style(self, name):
        self.patch_qs_style_name = name

    def set_patch_qs_rewrite(self, value):
        if value not in ["reverse", "predelete", "yes", "no", "warn", "abort"]:
            raise ValueError
        self.patch_qs_rewrite = value

    def set_patch_py_style(self, name):
        self.patch_py_style_name = name

    def set_patch_test_style(self, name):
        self.patch_test_style_name = name

    def set_patch_model_style(self, name):
        self.patch_model_style_name = name

    def set_patch_py_rewrite(self, value):
        if value not in ["reverse", "predelete", "yes", "no", "warn", "abort"]:
            raise ValueError
        self.patch_py_rewrite = value

    def set_patch_test_rewrite(self, value):
        if value not in ["reverse", "predelete", "yes", "no", "warn", "abort"]:
            raise ValueError
        self.patch_test_rewrite = value

    def set_patch_model_rewrite(self, value):
        if value not in ["reverse", "predelete", "yes", "no", "warn", "abort"]:
            raise ValueError
        self.patch_model_rewrite = value

    def enable_diff_xml_search_move(self):
        self.diff_xml_search_move = True

    def set_clean_patch(self):
        self.clean_patch = True

    # :::: ACTIONS ::::
    def do_build_project(self, buildxml):
        try:
            return projectbuilder.build_xml_file(self, buildxml)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_folder_diff(self, basedir, finaldir, patchdir):
        try:
            return flpatchdir.diff_folder(self, basedir, finaldir, patchdir)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_folder_patch(self, basedir, finaldir, patchdir):
        try:
            return flpatchdir.patch_folder(self, basedir, finaldir, patchdir)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_file_diff(self, ext, base, final):
        try:
            ext = str(ext).upper()
            if ext == "QS":
                return flpatchqs.diff_qs(self, base, final)
            if ext == "QSDIR":
                return flpatchqs.diff_qs_dir(self, base, final)
            if ext == "PY":
                aBase = base.split("/")
                nom = aBase[-1:][0]
                if nom.startswith("test_"):
                    return flpatchtest.diff_test(self, base, final)

                elif (
                    nom.endswith(("_api.py", "_schema.py", "_model.py", "_class.py"))
                    or nom.startswith("test_")
                    and nom.endswith(".py")
                ):
                    return flpatchapipy.diff_py(self, base, final)
                elif "models" in base or "pruebasqs" in base:
                    return flpatchmodel.diff_model(self, base, final)
                else:
                    return flpatchpy.diff_py(self, base, final)
            # if ext == 'XML': return flpatchxml.diff_xml(self,base,final)
            if ext == "XML":
                return flpatchlxml.diff_lxml(self, base, final)
            print("Unknown $ext %s" % (repr(ext)))
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_file_patch(self, ext, base, patch):
        try:
            ext = str(ext).upper()
            if ext == "QS":
                return flpatchqs.patch_qs(self, base, patch)
            if ext == "QSDIR":
                return flpatchqs.patch_qs_dir(self, base, patch)
            if ext == "PY":
                aBase = base.split("/")
                nom = aBase[-1:][0]
                if nom.startswith("test_"):
                    return flpatchtest.patch_test(self, base, patch)
                elif nom.endswith("_ut.py"):
                    return flpatchpy.patch_py(self, base, patch)
                elif nom.endswith("_def.py"):
                    return flpatchpy.patch_py(self, base, patch)
                elif (
                    nom.endswith(("_api.py", "_schema.py", "_model.py", "_class.py"))
                    or nom.startswith("test_")
                    and nom.endswith(".py")
                ):
                    return flpatchapipy.patch_py(self, base, patch)
                elif "models" in base or "pruebasqs" in base:
                    return flpatchmodel.patch_model(self, base, patch)
                else:
                    return flpatchpy.patch_py(self, base, patch)
            if ext == "XML":
                return flpatchlxml.patch_lxml(self, patch, base)
            print("Unknown $ext %s" % (repr(ext)))
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_file_check(self, check, filename):
        try:
            check = str(check).lower()
            if check == "qs-classes":
                return flpatchqs.check_qs_classes(self, filename)
            if check == "py-classes":
                return flpatchpy.check_py_classes(self, filename)
            if check == "test-classes":
                return flpatchtest.check_test_classes(self, filename)
            if check == "model-classes":
                return flpatchmodel.check_model_classes(self, filename)
            print("Unknown $check %s" % (repr(check)))
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_qs_extract(self, final, classlist):
        try:
            return flpatchqs.extract_classes_qs(self, final, classlist)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_qs_split(self, final):
        try:
            return flpatchqs.split_qs(self, final)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_qs_join(self, folder):
        try:
            return flpatchqs.join_qs(self, folder)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_py_extract(self, final, classlist):
        try:
            return flpatchpy.extract_classes_py(self, final, classlist)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_py_split(self, final):
        try:
            return flpatchpy.split_py(self, final)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_py_join(self, folder):
        try:
            return flpatchpy.join_py(self, folder)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_test_extract(self, final, classlist):
        try:
            return flpatchtest.extract_classes_test(self, final, classlist)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_test_split(self, final):
        try:
            return flpatchtest.split_test(self, final)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_test_join(self, folder):
        try:
            return flpatchtest.join_test(self, folder)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_model_extract(self, final, classlist):
        try:
            return flpatchmodel.extract_classes_model(self, final, classlist)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_model_split(self, final):
        try:
            return flpatchmodel.split_model(self, final)
        except Exception as e:
            self.exception(type(e).__name__, str(e))

    def do_model_join(self, folder):
        try:
            return flpatchmodel.join_model(self, folder)
        except Exception as e:
            self.exception(type(e).__name__, str(e))
