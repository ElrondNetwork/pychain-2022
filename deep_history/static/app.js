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
            element: $(".queries-view"),
            model: this.queriesModel,
            context: this.contextModel
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
        this.element.find("form").on("change", this.onChanged.bind(this));
    }

    onChanged() {
        const form = this.element.find("form");
        const data = formToObject(form);

        this.model.save(data);
    }

    render() {
        const data = this.model.load();
        this.element.find(`[name='network'][value='${data.network}']`).parent().button("toggle");
    }
}

class ContextModel {
    save(data) {
        localStorage.setItem("context", JSON.stringify(data));
        triggerEvent("contextSaved", data);
    }

    load() {
        const dataJson = localStorage.getItem("context") || "{}";
        const data = JSON.parse(dataJson);

        data.network = data.network || "devnet";
        return data;
    }
}

class QueriesView {
    setup(options) {
        this.element = options.element;
        this.model = options.model;
        this.context = options.context;

        this.setupEvents();
        this.render();
    }

    setupEvents() {
        onEvent("contextSaved", this.render.bind(this));

        this.element.find(".query button").on("click", this.onRunQueryClicked.bind(this));
    }

    async onRunQueryClicked(event) {
        const queryElement = $(event.target).parent();
        const url = this.buildUrl(queryElement);
        const response = await this.model.runQuery(url);
        this.renderResponse(response);
    }

    buildUrl(queryElement) {
        const urlElements = queryElement.find(".part");
        const urlParts = urlElements.map(function () {
            return $(this).text() || $(this).val();
        });

        const url = urlParts.get().join("");
        return url;
    }

    render() {
        const data = this.context.load();

        this.element.find(".part").attr("spellcheck", false);
        this.element.find("[data-toggle='tooltip']").tooltip();
        this.element.find(".part.network").text(data.network);
    };

    renderResponse(response) {
        const responseJson = JSON.stringify(response, null, 4);
        this.element.find(".response").html(responseJson);
    }
}


class QueriesModel {
    async runQuery(url) {
        try {
            const response = await axios.get(url);
            return response.data;
        } catch (error) {
            if (error.response) {
                return error.response.data;
            }

            return {
                error: error.toString()
            }
        }
    }
}
