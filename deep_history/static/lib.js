function triggerEvent(name, data) {
    $(document).trigger(name, data);
}

function onEvent(name, callback) {
    $(document).on(name, function (_, data) {
        callback(data);
    });
}

function offEvent(name, callback) {
    $(document).off(name, callback);
}

function formToObject(form) {
    const formArray = form.serializeArray();
    const formObject = {};

    for (const item of formArray) {
        const name = item["name"];
        const value = item["value"];
        formObject[name] = value;
    }

    // Handle checkboxes
    form.find("[type='checkbox']").each(function () {
        const checkbox = $(this);
        const name = checkbox.attr("name");
        formObject[name] = checkbox.prop("checked");
    });

    return formObject;
}

function toPrettyJson(obj) {
    return JSON.stringify(obj, null, 4);
}
