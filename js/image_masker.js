import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

function send_message(id, message, data) {
    const body = new FormData();
    body.append('id', id);
    body.append('message',message);
    if (data) body.append('data', data)
    api.fetchApi("/image_chooser_message", { method: "POST", body, });
}

function display_preview_images(node, urls) {
    node.imgs = [];
    urls.forEach((u)=> {
        const img = new Image();
        node.imgs.push(img);
        img.onload = () => { app.graph.setDirtyCanvas(true); };
        img.src = api.apiURL(`/view?filename=${encodeURIComponent(u.filename)}&type=temp&subfolder=${app.getPreviewFormatParam()}`);
    })
    node.setSizeForImage?.();
}

function open_mask_editor(node) {
    app.copyToClipspace(node)
    app.clipspace_return_node = node
    app.open_maskeditor()
}

app.registerExtension({
	name: "cg.custom.image_masker",

    setup() {
        const original_api_interrupt = api.interrupt;
        api.interrupt = function () {
            if (FlowState.paused() && !FlowState.cancelling) send_message(0,'cancel');
            original_api_interrupt.apply(this, arguments);
        }

        function earlyImageHandler(event) {
            const node = app.graph._nodes_by_id[event.detail.id];
            display_preview_images(node, event.detail.urls);
            node.imageIndex = 0;
            open_mask_editor(node);
        }
        api.addEventListener("image-masker-image", earlyImageHandler);

        const pasteFromClipspace = app.pasteFromClipspace;
        app.pasteFromClipspace = function(node) {
            send_message( id=node_id, message='mask_uploaded' )
            return pasteFromClipspace(node)
        }
    }, 

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType?.comfyClass === "Image Masker") {

        }
    }
})