#define Py_LIMITED_API 0x03080000
#define PY_SSIZE_T_CLEAN
#include <math.h>
#include <Python.h>



static PyObject* cycle_xor(PyObject* self, PyObject* args) {
    const unsigned char *input_bytes;
    Py_ssize_t input_len;
    const unsigned char *key_bytes;
    Py_ssize_t key_len;

    if (!PyArg_ParseTuple(args, "y#y#", &input_bytes, 
        &input_len, &key_bytes, &key_len)) return NULL;

    unsigned char *result = malloc(input_len);
    if (!result) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < input_len; i++) {
        result[i] = input_bytes[i] ^ key_bytes[i % key_len];
    }

    PyObject *output = PyBytes_FromStringAndSize(result, input_len);
    free(result);
    return output;
}

static PyObject* chunk_parser(PyObject* self, PyObject* args) {
    unsigned char *input_bytes;
    Py_ssize_t input_len;
    unsigned char block_use_bit;

    if (!PyArg_ParseTuple(args, "y#n", &input_bytes, &input_len, &block_use_bit)) return NULL;
    if (input_len <= 0 || input_len % 4 != 0) {
        PyErr_SetString(PyExc_ValueError, "input_len must be positive and divisible by 4");
        return NULL;
    }
    if (block_use_bit == 0 || block_use_bit > 32) {
        PyErr_SetString(PyExc_ValueError, "block_use_bit must be between 1 and 32");
        return NULL;
    }

    unsigned int *chunk_data_array = malloc(input_len);
    if (!chunk_data_array) return PyErr_NoMemory();
    Py_ssize_t chunk_data_len = input_len/4 ;
    for (unsigned short i = 0; i < chunk_data_len; i++) chunk_data_array[i] = 0;

    for (unsigned short i = 0; i < input_len; i++) {
        unsigned short j = i/4;
        chunk_data_array[j] <<= 8;
        chunk_data_array[j] |= input_bytes[i];
    }
    

    unsigned int chunk[4096];
    unsigned short index = 0;
    unsigned int block_count_in_4_bytes = 32 / block_use_bit;
    unsigned int and_oper = 0xffffffff >> (32 - block_use_bit);

    for (unsigned short i = 0; i < chunk_data_len; i++) {
        unsigned int data1 = chunk_data_array[i];
        for (unsigned short j = 0; j < block_count_in_4_bytes; j++)
        {   
            chunk[index] = data1 & and_oper;
            data1 >>= block_use_bit;
            index++;
            if (index >= 4096) break;
        }
        if (index >= 4096) break;
    }

    PyObject *output = PyList_New(4096);
    for (unsigned short i = 0; i < 4096; i++) {
        PyList_SetItem(output, i, PyLong_FromLong(chunk[i]));
    }
    return output;
}

static PyObject* chunk_serialize(PyObject* self, PyObject* args) {
    PyObject *input_list;
    Py_ssize_t block_len;

    if (!PyArg_ParseTuple(args, "On", &input_list, &block_len)) return NULL;
    if (PyList_Size(input_list) != 4096) { 
        PyErr_SetString(PyExc_TypeError, "input_list len must be 4096");
        return NULL;
    };
    if (block_len <= 0) {
        PyErr_SetString(PyExc_ValueError, "input_len must be positive");
        return NULL;
    }

    unsigned short block_use_bit = ceil( log2(block_len) );
    unsigned short block_count_in_4_bytes = 32 / block_use_bit;
    unsigned short chunk_data_len = ceil( 4096 / block_count_in_4_bytes );

    unsigned int *chunk_data_array = malloc(chunk_data_len * 4);
    if (!chunk_data_array) return PyErr_NoMemory();
    for (unsigned short i = 0; i < chunk_data_len; i++) chunk_data_array[i] = 0;

    unsigned short index = 0;
    for (unsigned short i = 0; i < chunk_data_len; i++) {   
        for (unsigned char j = 0; j < block_count_in_4_bytes; j++) {
            chunk_data_array[i] <<= block_use_bit;
            chunk_data_array[i] |= PyLong_AsLong(PyList_GetItem(input_list, index));
            index++;
            if (index >= 4096) break;
        }
        printf("%#x, ", chunk_data_array[i]); 
        if (index >= 4096) break;
    }

    PyObject *output = PyBytes_FromStringAndSize((char*)chunk_data_array, chunk_data_len * 4);
    free(chunk_data_array);
    return output;
}



static PyMethodDef Methods[] = {
    {"cycle_xor", cycle_xor, METH_VARARGS, "C API cycle xor operation"},
    {"chunk_parser", chunk_parser, METH_VARARGS, "C API fast parser chunk data"},
    {"chunk_serialize", chunk_serialize, METH_VARARGS, "C API fast serialize chunk data"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "MCBEWorld_C_API",
    NULL,
    -1,
    Methods
};

PyMODINIT_FUNC PyInit_MCBEWorld_C_API(void) {
    return PyModule_Create(&module);
}