import { C as CodeLoader } from "./vue-content-loader.es-7bca2d9b.js";
import ExcelTableConfig from "./readExcel-dabaf51b.js";
import CsvTableConfig from "./readCsv-e8359522.js";
import ParquetTableConfig from "./readParquet-e0771ef2.js";
import { u as useNodeStore } from "./vue-codemirror.esm-9ed00d50.js";
import { F as FileBrowser } from "./designer-bf3d9487.js";
import { d as defineComponent, r as ref, l as computed, b as resolveComponent, c as openBlock, e as createElementBlock, p as createBaseVNode, t as toDisplayString, h as createBlock, i as createCommentVNode, f as createVNode, w as withCtx, u as unref, _ as _export_sfc } from "./index-d0518598.js";
import "./dropDown-025888df.js";
const _hoisted_1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _hoisted_2 = { class: "listbox-wrapper" };
const _hoisted_3 = { class: "file-upload-container" };
const _hoisted_4 = {
  for: "file-upload",
  class: "file-upload-label"
};
const _hoisted_5 = { class: "file-label-text" };
const _hoisted_6 = { key: 0 };
const _hoisted_7 = { class: "listbox-wrapper" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Read",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const selectedFile = ref(null);
    const isExcelFile = ref(false);
    const isCsvFile = ref(false);
    const isParquetFile = ref(false);
    const nodeRead = ref(null);
    const dataLoaded = ref(false);
    const selectedPath = ref("");
    const modalVisibleForOpen = ref(false);
    const getDisplayFileName = computed(() => {
      var _a, _b, _c;
      if ((_a = selectedFile.value) == null ? void 0 : _a.name) {
        return selectedFile.value.name;
      }
      if ((_c = (_b = nodeRead.value) == null ? void 0 : _b.received_file) == null ? void 0 : _c.name) {
        return nodeRead.value.received_file.name;
      }
      return "Choose a file...";
    });
    const receivedExcelTable = ref({
      name: "",
      path: "",
      file_type: "excel",
      sheet_name: "",
      start_row: 0,
      start_column: 0,
      end_row: 0,
      end_column: 0,
      has_headers: true,
      type_inference: false
    });
    const receivedCsvTable = ref({
      name: "",
      path: "",
      file_type: "csv",
      reference: "",
      starting_from_line: 0,
      delimiter: ",",
      has_headers: true,
      encoding: "utf-8",
      row_delimiter: "",
      quote_char: "",
      infer_schema_length: 1e3,
      truncate_ragged_lines: false,
      ignore_errors: false
    });
    const receivedParquetTable = ref({
      name: "",
      path: "",
      file_type: "parquet"
    });
    const handleFileChange = (fileInfo) => {
      var _a;
      try {
        if (!fileInfo) {
          console.warn("No file info provided");
          return;
        }
        const fileType = (_a = fileInfo.name.split(".").pop()) == null ? void 0 : _a.toLowerCase();
        if (!fileType) {
          console.warn("No file type detected");
          return;
        }
        isExcelFile.value = false;
        isCsvFile.value = false;
        isParquetFile.value = false;
        switch (fileType) {
          case "xlsx":
            isExcelFile.value = true;
            receivedExcelTable.value.path = fileInfo.path;
            receivedExcelTable.value.name = fileInfo.name;
            break;
          case "csv":
          case "txt":
            isCsvFile.value = true;
            receivedCsvTable.value.path = fileInfo.path;
            receivedCsvTable.value.name = fileInfo.name;
            break;
          case "parquet":
            isParquetFile.value = true;
            receivedParquetTable.value.path = fileInfo.path;
            receivedParquetTable.value.name = fileInfo.name;
            break;
          default:
            console.warn("Unsupported file type:", fileType);
            return;
        }
        selectedFile.value = fileInfo;
        selectedPath.value = fileInfo.path;
        modalVisibleForOpen.value = false;
      } catch (error) {
        console.error("Error handling file change:", error);
      }
    };
    const loadNodeData = async (nodeId) => {
      var _a;
      try {
        const nodeResult = await nodeStore.getNodeData(nodeId, false);
        if (!nodeResult) {
          console.warn("No node result received");
          dataLoaded.value = true;
          return;
        }
        nodeRead.value = nodeResult.setting_input;
        if (((_a = nodeResult.setting_input) == null ? void 0 : _a.is_setup) && nodeResult.setting_input.received_file) {
          const { file_type } = nodeResult.setting_input.received_file;
          isExcelFile.value = false;
          isCsvFile.value = false;
          isParquetFile.value = false;
          switch (file_type) {
            case "excel":
              isExcelFile.value = true;
              receivedExcelTable.value = nodeResult.setting_input.received_file;
              break;
            case "csv":
              isCsvFile.value = true;
              receivedCsvTable.value = nodeResult.setting_input.received_file;
              break;
            case "parquet":
              isParquetFile.value = true;
              receivedParquetTable.value = nodeResult.setting_input.received_file;
              break;
          }
          selectedPath.value = nodeResult.setting_input.received_file.path;
        }
        dataLoaded.value = true;
      } catch (error) {
        console.error("Error loading node data:", error);
        dataLoaded.value = true;
      }
    };
    const pushNodeData = async () => {
      try {
        dataLoaded.value = false;
        if (!nodeRead.value) {
          console.warn("No node read value available");
          dataLoaded.value = true;
          return;
        }
        nodeRead.value.is_setup = true;
        if (isExcelFile.value) {
          nodeRead.value.received_file = receivedExcelTable.value;
        } else if (isCsvFile.value) {
          nodeRead.value.received_file = receivedCsvTable.value;
        } else if (isParquetFile.value) {
          nodeRead.value.cache_results = false;
          nodeRead.value.received_file = receivedParquetTable.value;
        }
        await nodeStore.updateSettings(nodeRead);
      } catch (error) {
        console.error("Error pushing node data:", error);
      } finally {
        dataLoaded.value = true;
      }
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      const _component_el_dialog = resolveComponent("el-dialog");
      return dataLoaded.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createBaseVNode("div", _hoisted_3, [
            createBaseVNode("div", {
              class: "file-upload-wrapper",
              onClick: _cache[0] || (_cache[0] = ($event) => modalVisibleForOpen.value = true)
            }, [
              createBaseVNode("label", _hoisted_4, [
                _cache[5] || (_cache[5] = createBaseVNode("i", { class: "fas fa-table file-icon" }, null, -1)),
                createBaseVNode("span", _hoisted_5, toDisplayString(getDisplayFileName.value), 1)
              ])
            ])
          ])
        ]),
        isCsvFile.value || isExcelFile.value || isParquetFile.value ? (openBlock(), createElementBlock("div", _hoisted_6, [
          createBaseVNode("div", _hoisted_7, [
            _cache[6] || (_cache[6] = createBaseVNode("div", { class: "listbox-subtitle" }, "File Specs", -1)),
            isExcelFile.value ? (openBlock(), createBlock(ExcelTableConfig, {
              key: 0,
              modelValue: receivedExcelTable.value,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => receivedExcelTable.value = $event)
            }, null, 8, ["modelValue"])) : createCommentVNode("", true),
            isCsvFile.value ? (openBlock(), createBlock(CsvTableConfig, {
              key: 1,
              modelValue: receivedCsvTable.value,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => receivedCsvTable.value = $event)
            }, null, 8, ["modelValue"])) : createCommentVNode("", true),
            isParquetFile.value ? (openBlock(), createBlock(ParquetTableConfig, {
              key: 2,
              modelValue: receivedParquetTable.value,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => receivedParquetTable.value = $event)
            }, null, 8, ["modelValue"])) : createCommentVNode("", true)
          ])
        ])) : createCommentVNode("", true),
        createVNode(_component_el_dialog, {
          modelValue: modalVisibleForOpen.value,
          "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => modalVisibleForOpen.value = $event),
          title: "Select a file to Read",
          width: "70%"
        }, {
          default: withCtx(() => [
            createVNode(FileBrowser, {
              "allowed-file-types": ["csv", "txt", "parquet", "xlsx"],
              mode: "open",
              onFileSelected: handleFileChange
            })
          ]),
          _: 1
        }, 8, ["modelValue"])
      ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 1 }));
    };
  }
});
const Read_vue_vue_type_style_index_0_scoped_41ef044d_lang = "";
const Read = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-41ef044d"]]);
export {
  Read as default
};
