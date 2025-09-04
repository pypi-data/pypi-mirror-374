import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";
const styleMenus = `
    .p-panel-content-container{
        display: none;
    }
    // .side-tool-bar-container.small-sidebar{
    //     display: none;
    // }
    .comfyui-menu.flex.items-center{
        display: none;
    }
    .p-dialog-mask.p-overlay-mask.p-overlay-mask-enter.p-dialog-bottomright{
        display: none !important;
    }
    body .bizyair-comfy-floating-button{
        display: none;
    }
    .bizy-select-title-container{
        display: none;
    }
    .workflow-tabs-container{
        display: none;
    }
    body .comfyui-body-bottom{
        display: none;
    }
    #comfyui-body-bottom{
        display: none;
    }

    .p-button.p-component.p-button-icon-only.p-button-text.workflows-tab-button.side-bar-button.p-button-secondary{
        display: none;
    }
    .p-button.p-component.p-button-icon-only.p-button-text.mtb-inputs-outputs-tab-button.side-bar-button.p-button-secondary{
        display: none;
    }
    body div.side-tool-bar-end{
        display: none;
    }
    body .tydev-utils-log-console-container{
        display: none;
    }
    .p-dialog-mask.p-overlay-mask.p-overlay-mask-enter[data-pc-name="dialog"]{
        display: none !important;
    }
    .p-button.p-component.p-button-icon-only.p-button-text.templates-tab-button.side-bar-button.p-button-secondary{
        display: none;
    }
    .p-button.p-component.p-button-icon-only.p-button-text.queue-tab-button.side-bar-button.p-button-secondary{
        display: none;
    }
`;
app.registerExtension({
  name: "comfy.BizyAir.Style",
  async setup() {
    $el("style", {
      textContent: styleMenus,
      parent: document.head,
    });
    const getCloseBtn = () => {
        let temp = null
        document.querySelectorAll('h3').forEach(e => {
            if (e.innerHTML == "<span>从模板开始</span>") {
                temp = e.parentNode.parentNode.querySelector('.p-dialog-close-button')
            }
        })
        return temp
    }
    let index = 0
    let iTimer = setInterval(() => {
        index++
        if (index > 10) {
            clearInterval(iTimer)
            return
        }
        if (getCloseBtn()) {
            getCloseBtn().click()
            clearInterval(iTimer)
        }
    }, 300)
  }
});
