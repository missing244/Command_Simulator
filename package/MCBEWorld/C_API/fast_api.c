#define Py_LIMITED_API 0x03080000
#define PY_SSIZE_T_CLEAN
#include <Python.h>



static PyObject* cycle_xor(PyObject* self, PyObject* args) {
    const char *input_bytes;
    Py_ssize_t input_len;
    const char *key_bytes;
    Py_ssize_t key_len;

    if (!PyArg_ParseTuple(args, "y#y#", &input_bytes, 
        &input_len, &key_bytes, &key_len)) return NULL;

    char *result = (char*)malloc(input_len);
    if (!result) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < input_len; i++) {
        result[i] = input_bytes[i] ^ key_bytes[i % key_len];
    }

    PyObject *output = PyBytes_FromStringAndSize(result, input_len);
    free(result);
    return output;
}

static PyObject* chunk_parser(PyObject* self, PyObject* args) {
    const char *input_bytes;
    Py_ssize_t input_len;

    if (!PyArg_ParseTuple(args, "y#", &input_bytes, &input_len)) return NULL;

    char *result = (char*)malloc(input_len);
    if (!result) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < input_len; i++) {
        result[i] = input_bytes[i] ^ key_bytes[i % key_len];
    }

    PyObject *output = PyBytes_FromStringAndSize(result, input_len);
    free(result);
    return output;
}



static PyMethodDef Methods[] = {
    {"cycle_xor", cycle_xor, METH_VARARGS, "Perform cyclic XOR on bytes"},
    {"chunk_parser", chunk_parser, METH_VARARGS, "Perform cyclic XOR on bytes"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef xormodule = {
    PyModuleDef_HEAD_INIT,
    "MCBEWorld_C_API",
    NULL,
    -1,
    Methods
};

PyMODINIT_FUNC PyInit_MCBEWorld_C_API(void) {
    return PyModule_Create(&xormodule);
}