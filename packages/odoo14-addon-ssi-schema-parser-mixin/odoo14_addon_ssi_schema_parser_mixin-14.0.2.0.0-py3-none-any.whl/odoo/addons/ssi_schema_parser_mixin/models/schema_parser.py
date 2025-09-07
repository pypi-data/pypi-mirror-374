import json
import os
import tempfile
from typing import Any, Dict, List, Optional

import yaml
from json_schema_for_humans.generate import generate_from_schema
from json_schema_for_humans.generation_configuration import GenerationConfiguration

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval

try:
    from jsonschema import Draft202012Validator, SchemaError, ValidationError

    _HAS_JSONSCHEMA = True
except Exception:
    _HAS_JSONSCHEMA = False


class SchemaParser(models.Model):
    _name = "schema_parser"
    _description = "Schema Parser"
    _inherit = "mixin.master_data"

    category_id = fields.Many2one(
        comodel_name="schema_parser_category",
        string="Category",
        ondelete="restrict",
        index=True,
    )
    schema = fields.Text(
        help="Validation schema (JSON Schema). Supports JSON or YAML text.",
    )
    schema_valid = fields.Boolean(
        string="Valid Schema",
        compute="_compute_schema_valid",
        store=True,
        compute_sudo=True,
    )
    schema_error = fields.Text(
        string="Schema Error message",
        compute="_compute_schema_valid",
        store=True,
        compute_sudo=True,
    )
    parser = fields.Text(
        string="Specification",
        help="Specification to be validated and parsed. Supports JSON or YAML text.",
    )
    documentation = fields.Text(
        string="Documentation",
        compute="_compute_documentation",
        store=True,
        compute_sudo=True,
        help="""Auto-generated (Markdown/HTML) from JSON Schema in the `schema`
field using json-schema-for-humans when available; otherwise a minimal Markdown fallback.""",
    )
    schema_example = fields.Text(
        string="Example",
    )
    example_is_valid = fields.Boolean(
        compute="_compute_result_example",
    )
    example_error_message = fields.Text(
        compute="_compute_result_example",
    )
    result_example = fields.Text(
        compute="_compute_result_example",
    )
    result_example_is_valid = fields.Boolean(
        string="Parsing Succeed",
        compute="_compute_result_example",
    )
    result_example_error_message = fields.Text(
        string="Parsing Error Message",
        compute="_compute_result_example",
    )

    @api.depends("schema", "schema_valid", "schema_error")
    def _compute_documentation(self):
        for rec in self:
            rec.documentation = ""

            schema_obj, err = rec._json_try_load(rec.schema or "")
            if err or not isinstance(schema_obj, dict):
                rec.documentation = "**Schema Documentation**\n\n" + (
                    rec.schema_error
                    or f"> Gagal mem-parsing schema sebagai JSON.\n> {err}"
                )
                continue

            tmp_path = None
            try:
                # 1) Tulis schema ke file sementara
                with tempfile.NamedTemporaryFile(
                    "w", suffix=".json", delete=False, encoding="utf-8"
                ) as tf:
                    json.dump(schema_obj, tf, ensure_ascii=False, indent=2)
                    tmp_path = tf.name

                # 2) Konfigurasi output (Markdown). Gunakan "js"/"flat" untuk HTML.
                cfg = GenerationConfiguration(
                    template_name="md",  # "md" => Markdown; "js"/"flat" => HTML
                    collapse_long_descriptions=False,
                    description_is_markdown=True,  # relevan untuk template HTML
                    show_toc=False,
                )

                # 3) Bangkitkan dokumentasi dari path file
                doc_text = generate_from_schema(tmp_path, config=cfg)

                rec.documentation = str(doc_text) if doc_text is not None else ""
            except Exception as e:
                rec.documentation = (
                    "**Schema Documentation**\n\n"
                    f"> Terjadi kesalahan saat menghasilkan dokumentasi: {e}"
                )
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        # Abaikan kegagalan hapus file temp
                        pass

    @api.depends(
        "schema",
        "parser",
        "schema_example",
    )
    def _compute_result_example(self):
        for record in self:
            # Default/reset
            record.example_is_valid = True
            record.example_error_message = ""
            record.result_example_is_valid = True
            record.result_example_error_message = ""
            record.result_example = False

            if record.schema and record.parser and record.schema_example:
                # 1) Validasi spec (schema_example YAML) terhadap JSON Schema (schema)
                (_data, ex_valid, ex_err) = record.validate_against_schema(
                    record.schema_example
                )
                record.example_is_valid = ex_valid
                record.example_error_message = ex_err or ""

            if record.parser and record.schema_example:
                # 2) Parsing specification (tetap seperti perilaku sebelumnya)
                (result, res_valid, res_err) = record.parse_specification(
                    record.schema_example
                )
                record.result_example_is_valid = res_valid
                record.result_example_error_message = res_err or ""
                if res_valid and result is not None:
                    if isinstance(result, (dict, list)):
                        record.result_example = json.dumps(
                            result, ensure_ascii=False, indent=2
                        )
                    else:
                        record.result_example = str(result)

    def _json_try_load(self, text):
        """Parse JSON tanpa raise: kembalikan (obj, err_msg)."""
        if not text:
            return None, ""
        try:
            return json.loads(text), ""
        except Exception as e:
            return None, str(e)

    @api.depends("schema")
    def _compute_schema_valid(self):
        for record in self:
            # Default: invalid sampai semua cek lulus
            record.schema_error = ""
            record.schema_valid = False

            # 1) Pastikan schema valid JSON
            schema_obj, err = self._json_try_load(record.schema)
            if err:
                record.schema_error = (
                    _("Gagal mem-parsing schema sebagai JSON.\n%s") % err
                )
                continue
            if not isinstance(schema_obj, dict):
                record.schema_error = _(
                    "Schema JSON harus berupa object/dict pada level teratas."
                )
                continue

            # 2) Validasi struktur JSON Schema (jika lib tersedia)
            if _HAS_JSONSCHEMA:
                try:
                    Draft202012Validator.check_schema(schema_obj)
                except SchemaError as e:
                    record.schema_error = _("JSON Schema tidak valid:\n%s") % e
                    continue

            # Semua cek lulus
            record.schema_valid = True

    def validate_against_schema(self, data_text=None):
        """
        Validasi spec (YAML) terhadap JSON Schema (di field `schema`).
        Return: (result, is_valid, error_message)
        - result: object hasil parse YAML (dict) bila parse sukses, else None
        - is_valid: bool
        - error_message: string kosong jika valid, atau pesan error bila invalid
        """
        self.ensure_one()
        result = None
        is_valid = True
        error_message = ""

        # 1) Ambil dan cek schema (JSON)
        schema_obj, err = self._json_try_load(self.schema)
        if err or not isinstance(schema_obj, dict):
            return (
                None,
                False,
                _("Schema harus JSON yang valid: %s") % (err or _("bukan object")),
            )

        if not _HAS_JSONSCHEMA:
            return (
                None,
                False,
                _(
                    "Dependensi 'jsonschema' tidak tersedia. "
                    "Instal paket 'jsonschema' untuk validasi."
                ),
            )

        try:
            Draft202012Validator.check_schema(schema_obj)
        except SchemaError as e:
            return (
                None,
                False,
                _("JSON Schema tidak valid:\n%s") % e,
            )

        # 2) Ambil data (spec tetap YAML)
        try:
            data_obj = yaml.safe_load(data_text or self.schema_example)
        except Exception as e:
            return (
                None,
                False,
                _("Gagal mem-parsing data/spec sebagai YAML.\n%s") % e,
            )

        result = data_obj

        # 3) Validasi data vs JSON Schema
        try:
            Draft202012Validator(schema_obj).validate(data_obj)
        except ValidationError as e:
            is_valid = False
            error_message = _("Data tidak sesuai JSON Schema:\n%s") % e

        return (result, is_valid, error_message)

    def parse_specification(
        self,
        specification,
        additional_dict=None,
        supress_error=False,
    ):
        self.ensure_one()
        result = error_message = ""
        is_valid = True
        localdict = {
            "yaml_safe_load": yaml.safe_load,
            "yaml_safe_dump": yaml.safe_dump,
            "json_dumps": json.dumps,
            "json_loads": json.loads,
            "Any": Any,
            "Dict": Dict,
            "List": List,
            "Optional": Optional,
            "specification": specification,
        }
        if additional_dict is not None:
            localdict.update(additional_dict)
        try:
            safe_eval(self.parser, localdict, mode="exec", nocopy=True)
            result = localdict.get("result")
            if result is None:
                is_valid = False
                error_message = _("Parser did not set `result`.")
        except Exception as error:
            is_valid = False
            error_message = _("Error executing parser.\n%s") % error

        return (result, is_valid, error_message)
