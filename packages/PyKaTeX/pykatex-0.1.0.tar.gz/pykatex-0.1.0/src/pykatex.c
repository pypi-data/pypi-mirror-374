#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "katex.h"


static PyObject *ParseError;

// wrapper for Python
static PyObject* py_renderToString(PyObject *self, PyObject *args, PyObject *kwargs) {
    KatexOptions katex_options = {0};

    PyObject *displayModeObj = NULL, *leqnoObj = NULL, *fleqnObj = NULL, *throwOnErrorObj = NULL, *minRuleThicknessObj = NULL, *colorIsTextColorObj = NULL, *maxSizeObj = NULL, *maxExpandObj = NULL, *strictObj = NULL, *trustObj = NULL, *globalGroupObj = NULL;
    char *input, *output = NULL, *errorColor = NULL;

    static char *kwlist[] = {"input", "displayMode", "output", "leqno", "fleqn", "throwOnError", "errorColor", "minRuleThickness", "colorIsTextColor", "maxSize", "maxExpand", "strict", "trust", "globalGroup", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s|O!sO!O!O!sOO!OOOO!O!", kwlist, &input, &PyBool_Type, &displayModeObj, &output, &PyBool_Type, &leqnoObj, &PyBool_Type, &fleqnObj, &PyBool_Type, &throwOnErrorObj, &errorColor, &minRuleThicknessObj, &PyBool_Type, &colorIsTextColorObj, &maxSizeObj, &maxExpandObj, &strictObj, &PyBool_Type, &trustObj, &PyBool_Type, &globalGroupObj))
    {
        return NULL;
    }

    bool t = true, f = false;
    if (displayModeObj != NULL) {
        katex_options.display_mode = displayModeObj == Py_True ? &t : &f;
    }
    if (output != NULL) {
        katex_options.output = output;
    }
    if (leqnoObj != NULL) {
        katex_options.leqno = leqnoObj == Py_True ? &t : &f;
    }
    if (fleqnObj != NULL) {
        katex_options.fleqn = fleqnObj == Py_True ? &t : &f;
    }
    if (throwOnErrorObj != NULL) {
        katex_options.throw_on_error = throwOnErrorObj == Py_True ? &t : &f;
    }
    if (errorColor != NULL) {
        katex_options.error_color = errorColor;
    }
    if (minRuleThicknessObj != NULL) {
        double minRuleThickness = PyFloat_AsDouble(minRuleThicknessObj);
        if (PyErr_Occurred() != NULL) {
            return NULL;
        }
        katex_options.min_rule_thickness = &minRuleThickness;
    }
    if (colorIsTextColorObj != NULL) {
        katex_options.color_is_text_color = colorIsTextColorObj == Py_True ? &t : &f;
    }
    if (maxSizeObj != NULL) {
        double maxSize = PyFloat_AsDouble(maxSizeObj);
        if (PyErr_Occurred() != NULL) {
            return NULL;
        }
        katex_options.max_size = &maxSize;
    }
    if (maxExpandObj != NULL) {
        double maxExpand = PyFloat_AsDouble(maxExpandObj);
        if (PyErr_Occurred() != NULL) {
            return NULL;
        }
        katex_options.max_expand = &maxExpand;
    }
    if (strictObj != NULL && PyUnicode_Check(strictObj)) {
        const char *strictStr = PyUnicode_AsUTF8(strictObj);
        if (!strictStr) {
            return NULL;
        }
        katex_options.strictStr = strictStr;
    } else if (strictObj != NULL && PyBool_Check(strictObj)) {
        katex_options.strictBool = strictObj == Py_True ? &t : &f;
    } else if (strictObj != NULL) {
        PyErr_SetString(PyExc_TypeError, "argument 'strict' must have str or bool value");
        return NULL;
    }
    if (trustObj) {
        katex_options.trust = trustObj == Py_True ? &t : &f;
    }
    if (trustObj) {
        katex_options.trust = trustObj == Py_True ? &t : &f;
    }
    if (globalGroupObj) {
        katex_options.global_group = globalGroupObj == Py_True ? &t : &f;
    }

    char *c_result = katex_renderToString(input, &katex_options);
    if (c_result == NULL) {
        JSException *exception = katex_get_last_error();

        // KaTeX always reports parse errors, and its messages begin with "KaTeX parse error: "
        // Since Python exceptions already include the exception type in their prefix, we strip
        // this redundant prefix by passing a pointer to exception->message + 19
        PyErr_SetString(ParseError, &exception->message[19]);
        return NULL;
    }

    PyObject *result = PyUnicode_FromString(c_result);
    if (result == NULL) {
        return NULL;
    }

    free(c_result);

    return result;
}

static PyMethodDef Methods[] = {
    {"renderToString", (PyCFunction)py_renderToString, METH_VARARGS | METH_KEYWORDS, "Print hello"},  // TODO(Ruben): write the docstring
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "pykatex",
    NULL,  // TODO(Ruben): add docstring
    -1,
    Methods
};

PyMODINIT_FUNC PyInit_pykatex(void) {
    PyObject *m = PyModule_Create(&module);
    if (!m) {
        return NULL;
    }

    if (PyModule_AddStringConstant(m, "OUTPUT_HTML", "html") < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddStringConstant(m, "OUTPUT_MATHML", "mathml") < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddStringConstant(m, "OUTPUT_HTML_AND_MATHML", "htmlAndMathml") < 0) {
        Py_DECREF(m);
        return NULL;
    }

    if (PyModule_AddStringConstant(m, "STRICT_IGNORE", "ignore") < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddStringConstant(m, "STRICT_WARN", "warn") < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddStringConstant(m, "STRICT_ERROR", "error") < 0) {
        Py_DECREF(m);
        return NULL;
    }

    ParseError = PyErr_NewException("pykatex.ParseError", NULL, NULL);
    if (ParseError == NULL) {
        return NULL;
    }
    Py_INCREF(ParseError);
    PyModule_AddObject(m, "ParseError", ParseError);

    return m;
}
