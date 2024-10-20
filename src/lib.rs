use pyo3::prelude::*;
use pyo3::types::{PyClass, PyList};
use pyo3::exceptions::PyTypeError;
use std::collections::{HashSet, HashMap};
use std::sync::{Arc, Mutex};
use std::sync::LazyLock;
use std::any::TypeId;
use std::hash::Hash;
use std::any::Any;

// A dynamic cache to store memoized sets of arbitrary types
struct MemoizationCache {
    cache: Mutex<HashMap<TypeId, Box<dyn Any + Send + Sync>>>,
}

impl MemoizationCache {
    fn new() -> Self {
        MemoizationCache {
            cache: Mutex::new(HashMap::new()),
        }
    }

    // Get or initialize a memoized value by type
    fn get_or_insert<T: 'static + Send + Sync, F: FnOnce() -> T>(&self, init: F) -> Arc<T> {
        let mut cache = self.cache.lock().unwrap();
        let type_id = TypeId::of::<T>();

        if let Some(value) = cache.get(&type_id) {
            value.downcast_ref::<Arc<T>>().unwrap().clone()
        } else {
            let new_value = Arc::new(init());
            cache.insert(type_id, Box::new(new_value.clone()));
            new_value
        }
    }
}

// A global memoization cache, lazily initialized with std::sync::LazyLock
static CACHE: LazyLock<MemoizationCache> = LazyLock::new(MemoizationCache::new);

// Utility function to create an immutable Arc<HashSet>
fn arc_hashset<T: Eq + Hash>(elements: HashSet<T>) -> Arc<HashSet<T>> {
    Arc::new(elements)
}

// ----- BASE PRIMITIVE SETS -----
fn int_params() -> Arc<HashSet<i64>> {
    CACHE.get_or_insert(|| {
        let mut set = HashSet::new();
        set.insert(0);
        set.insert(1);
        set.insert(-1);
        set.insert(2);
        set.insert(-2);
        set.insert(2147483647);
        set.insert(-2147483648);
        set.insert(9223372036854775807);
        set.insert(-9223372036854775808);
        set
    })
}

fn bool_params() -> Arc<HashSet<bool>> {
    CACHE.get_or_insert(|| {
        let mut set = HashSet::new();
        set.insert(true);
        set.insert(false);
        set
    })
}

fn str_params() -> Arc<HashSet<&'static str>> {
    CACHE.get_or_insert(|| {
        let mut set = HashSet::new();
        set.insert("hello");
        set.insert("world");
        set
    })
}

// ----- COMPLEX TYPE HANDLING -----

// Recursively transform a set of T into a set of Vec<T>, ensuring T is Send + Sync
fn set_to_list<T: Clone + Eq + Hash + 'static + Send + Sync>(input_set: &HashSet<T>) -> Arc<HashSet<Vec<T>>> {
    CACHE.get_or_insert(|| {
        input_set.iter().map(|item| vec![item.clone()]).collect()
    })
}

// Recursively transform a set of (K, V) into a Vec of dicts (HashMap<K, V>), ensuring K and V are Send + Sync
fn set_to_dict<K: Clone + Eq + Hash + 'static + Send + Sync, V: Clone + Eq + Hash + 'static + Send + Sync>(
    key_set: &HashSet<K>, value_set: &HashSet<V>
) -> Arc<Vec<HashMap<K, V>>> {
    CACHE.get_or_insert(|| {
        key_set.iter().flat_map(|k| {
            value_set.iter().map(move |v| {
                let mut map = HashMap::new();
                map.insert(k.clone(), v.clone());
                map
            })
        }).collect()
    })
}

// ----- TYPE REGISTRY -----

// Define a function signature type for handlers that generate memoized sets
type TypeHandler = fn(Python) -> PyResult<PyObject>;

// A global registry mapping Python types to their corresponding handlers
static TYPE_REGISTRY: LazyLock<Mutex<HashMap<TypeId, TypeHandler>>> = LazyLock::new(|| {
    let mut m = HashMap::new();
    m.insert(TypeId::of::<pyo3::types::PyInt>(), get_int_set as TypeHandler);
    m.insert(TypeId::of::<pyo3::types::PyBool>(), get_bool_set as TypeHandler);
    m.insert(TypeId::of::<pyo3::types::PyString>(), get_str_set as TypeHandler);
    Mutex::new(m)
});

// Handler functions to return sets for primitive types
fn get_int_set(py: Python) -> PyResult<PyObject> {
    let int_set = int_params();
    Ok(hashset_to_pylist(py, &*int_set))
}

fn get_bool_set(py: Python) -> PyResult<PyObject> {
    let bool_set = bool_params();
    Ok(hashset_to_pylist(py, &*bool_set))
}

fn get_str_set(py: Python) -> PyResult<PyObject> {
    let str_set = str_params();
    Ok(hashset_to_pylist(py, &*str_set))
}

// Converts a HashSet to a PyList to return to Python
fn hashset_to_pylist<T: ToPyObject + Clone>(py: Python, set: &HashSet<T>) -> PyObject {
    PyList::new_bound(py, set.iter().cloned()).to_object(py)
}

// Converts a Vec of HashMaps to a PyList to return to Python
fn vec_of_dicts_to_pylist<K: ToPyObject + Hash + Clone + Eq, V: ToPyObject + Clone>(py: Python, vec: &Vec<HashMap<K, V>>) -> PyObject {
    PyList::new_bound(py, vec.iter().cloned()).to_object(py)
}

// ----- PYTHON BINDINGS -----

#[pyfunction]
fn iter_instances(py: Python, py_type: &PyClass) -> PyResult<PyObject> {
    // Get the TypeId for the Python type
    let type_id = py_type.type_id();

    // Lookup the handler for the Python type from the registry
    let registry = TYPE_REGISTRY.lock().unwrap();

    if let Some(handler) = registry.get(&type_id) {
        // Call the corresponding handler function
        handler(py)
    } else {
        // Unsupported type
        Err(PyTypeError::new_err("Unsupported type"))
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn pytest_static_stuff(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(iter_instances, m)?)?;
    Ok(())
}
