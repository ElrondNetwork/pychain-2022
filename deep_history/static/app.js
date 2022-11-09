class Application {
    constructor() {
        this.contextModel = new ContextModel();
        this.contextView = new ContextView();
        this.queriesModel = new QueriesModel();
        this.queriesView = new QueriesView();
    }

    async main() {
        this.contextView.setup({
            element: $(".context-view"),
            model: this.contextModel
        });

        this.queriesView.setup({

        });

        onEvent("contextSaved", function (data) {
        });
    }
}

class ContextView {
    setup(options) {
        this.element = options.element;
        this.model = options.model;

        this.setupEvents();
        this.render();
    }

    setupEvents() {
        this.element.find("form").on("submit", function () { return false; })
        this.element.find("[name='network']").on("change", this.onChanged.bind(this));
        this.element.find("[name='accountAddress']").on("change", this.onChanged.bind(this));
        this.element.find("[name='dateTime']").on("change", this.onChanged.bind(this));
    }

    onChanged() {
        const form = this.element.find("form");
        const data = formToObject(form);

        this.model.save(data);
        this.render();
    }

    render() {
        const data = this.model.load();
        this.element.find("[name='network']").prop("checked", false);
        this.element.find(`[name='network'][value='${data.network}']`).prop("checked", true);
        this.element.find("[name='accountAddress']").val(data.accountAddress);
        this.element.find("[name='dateTime']").val(data.dateTime);
    }
}

class ContextModel {
    defaultState = {
        network: "devnet",
        dateTime: "2022-11-01T00:00"
    };

    save(data) {
        console.info("ContextModel.save()");
        console.info(data);

        localStorage.setItem("context", JSON.stringify(data));
        triggerEvent("contextSaved", data);
    }

    load() {
        const dataJson = localStorage.getItem("context");
        if (!dataJson) {
            return this.defaultState;
        }

        const data = JSON.parse(dataJson);
        return data;
    }
}

class QueriesView {
    setup(options) {
        this.element = options.element;
        this.model = options.model;

        this.setupEvents();
        this.render();
    }

    setupEvents() {

    }

    render() {
    }
}

class QueriesModel {
    defaultState = {
    };

    save(data) {
        console.info("QueriesModel.save()");
        console.info(data);

        localStorage.setItem("queries", JSON.stringify(data));
        triggerEvent("queriesSaved", data);
    }

    load() {
        const dataJson = localStorage.getItem("queries");
        if (!dataJson) {
            return this.defaultState;
        }

        const data = JSON.parse(dataJson);
        return data;
    }
}
