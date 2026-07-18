# Adjudication Policy Ablation

- Timestamp: `20260718T200307Z`
- Raw run: `results\run_20260718T182612Z_cooper_raw.json`
- Structured run: `results\run_20260718T182612Z_cooper_structured.json`

Policies:
- **A_current_escalation** — Current policy: any disagreement or weak overlap escalates
- **B_majority_vote** — Plain majority vote over successful models
- **C_evidence_weighted** — Evidence-weighted adjudication (rationale scoring)

## Raw representation

| Policy | Coverage | Escalations | Accuracy | Precision | Recall | F1 | Avg rationale | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A_current_escalation | 6.2% | 15/16 (93.8%) | 6.2% | 100.0% | 100.0% | 100.0% | n/a | n/a |
| B_majority_vote | 100.0% | 0/16 (0.0%) | 56.2% | 56.2% | 100.0% | 72.0% | n/a | n/a |
| C_evidence_weighted | 87.5% | 2/16 (12.5%) | 56.2% | 66.7% | 88.9% | 76.2% | 0.577 | 6.80ms |

### Per-pair decisions (policy C)

- **pair_01_dottxt_ai_outlines_t1655_f9v10** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.62).
  - gemma3:4b: conflict (conf 0.95, score 0.41, grounded: sha)
  - deepseek-coder:6.7b: conflict (conf 0.50, score 0.19, grounded: hash_sha256)
  - llama3.2:3b: conflict (conf 0.80, score 0.62, grounded: braces, curly, format, guid, hash_sha256)
- **pair_02_dottxt_ai_outlines_t1655_f3v9** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 2 models agree on 'conflict' (best rationale score 0.48).
  - deepseek-coder:6.7b: conflict (conf 0.50, score 0.43, grounded: braces, curly, style, windows)
  - llama3.2:3b: conflict (conf 0.80, score 0.48, grounded: decimal, guid, octal_str)
- **pair_03_dspy_t8587_f3v5** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.81).
  - gemma3:4b: conflict (conf 0.95, score 0.81, grounded: actual, allow_reuse, buffer, contain, dspy, enabled, functionality, listeners, log, logging, long, message, mock, mode, previews, reset, reuse, reuse_stream, simulate, state, streaming, test_stream_listener_debug_logging_performance_guardrails, test_stream_listener_debug_no_runtime_behavior_change, test_stream_listener_debug_safe_truncation, truncated, truncation)
  - deepseek-coder:6.7b: conflict (conf 1.00, score 0.75, grounded: actual, avoid, buffer, correctly, enabled, formatting, info, large, level, logger, logs, previews, safely, streaming, test_stream_listener_debug_logging_performance_guardrails, test_stream_listener_debug_safe_truncation, truncated)
  - llama3.2:3b: conflict (conf 0.80, score 0.50, grounded: allow_reuse, enabled, enables, performance, state)
- **pair_04_dspy_t8563_f1v2** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 2 models agree on 'conflict' (best rationale score 0.72).
  - gemma3:4b: conflict (conf 0.95, score 0.72, grounded: arguments, convert_input_schema_to_tool_args, parse_python_calls, parsing, positional, test_parse_python_calls_basic, test_parse_python_calls_multiple, toolcalls, variable)
  - llama3.2:3b: conflict (conf 0.80, score 0.54, grounded: ast, extract, parse, parsing, python, syntax, tree)
- **pair_07_huggingface_datasets_t6252_f3v5** (truth: conflict) — A=escalate, B=conflict, C=conflict via `rationale_dominance`
  - llama3.2:3b gave the strongest grounded rationale (score 0.59 vs 0.00, margin 0.59 >= 0.12); verdict 'conflict' accepted over deepseek-coder:6.7b despite the vote split. Grounded evidence: ['as_array', 'decode_example', 'float32', 'image', 'max_resolution', 'parameter', 'pil', 'size'].
  - gemma3:4b: conflict (conf 0.95, score 0.56, grounded: as_array, decode_example, decoded, float32, image, max, max_resolution, parameter, pil)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.00, grounded: none)
  - llama3.2:3b: conflict (conf 0.80, score 0.59, grounded: as_array, decode_example, float32, image, max_resolution, parameter, pil, size)
- **pair_08_huggingface_datasets_t6252_f1v3** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `rationale_dominance`
  - llama3.2:3b gave the strongest grounded rationale (score 0.53 vs 0.00, margin 0.53 >= 0.12); verdict 'conflict' accepted over deepseek-coder:6.7b despite the vote split. Grounded evidence: ['exif', 'image', 'max_resolution', 'optional', 'orientation', 'parameter', 'size'].
  - gemma3:4b: conflict (conf 0.95, score 0.46, grounded: exif_transpose, imageops, max_resolution, optional, orientation, parameter, pil, rotated, thumbnail)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.00, grounded: none)
  - llama3.2:3b: conflict (conf 0.80, score 0.53, grounded: exif, image, max_resolution, optional, orientation, parameter, size)
- **pair_09_llama_index_t18813_f1v3** (truth: conflict) — A=escalate, B=conflict, C=conflict via `rationale_dominance`
  - llama3.2:3b gave the strongest grounded rationale (score 0.77 vs 0.44, margin 0.33 >= 0.12); verdict 'conflict' accepted over deepseek-coder:6.7b despite the vote split. Grounded evidence: ['bytes', 'resolve_audio_with_size', 'resolve_document_with_size', 'resolve_image_with_size', 'zero'].
  - gemma3:4b: conflict (conf 0.95, score 0.44, grounded: check, returned, size, valueerror, zero)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.44, grounded: resolve, returned, size, zero)
  - llama3.2:3b: conflict (conf 0.80, score 0.77, grounded: bytes, resolve_audio_with_size, resolve_document_with_size, resolve_image_with_size, zero)
- **pair_10_llama_index_t17244_f3v4** (truth: no_conflict) — A=escalate, B=conflict, C=no_conflict via `weighted_evidence_vote`
  - Rationale quality is comparable (margin 0.05 < 0.12); confidence-weighted evidence favors 'no_conflict' (conflict=0.57 vs no_conflict=0.62, gap 0.05).
  - gemma3:4b: conflict (conf 0.85, score 0.67, grounded: base64, encoding, explicitly, force_mimetype, guessing, imageblock, mime, normalize_image_bytes, override, resolve_image)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.62, grounded: directly, force_mimetype, normalize_image_bytes, override, resolve_image)
  - llama3.2:3b: conflict (conf 0.80, score 0.66, grounded: base64, encoded, force_mimetype, normalize_image_bytes, resolve_image)
- **pair_11_openai_tiktoken_t0_f1v3** (truth: conflict) — A=escalate, B=conflict, C=conflict via `weighted_evidence_vote`
  - Rationale quality is comparable (margin 0.12 < 0.12); confidence-weighted evidence favors 'conflict' (conflict=0.60 vs no_conflict=0.52, gap 0.08).
  - gemma3:4b: conflict (conf 0.95, score 0.63, grounded: analyze_frequency, bool, count, dictionary, encode, encoding, exceeds, frequencies, frequency, int, limit, list, max_tokens, number, parameter, raise, returns, set, tiktoken, token, valueerror)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.52, grounded: analyze_frequency, encoded, encoding, max_tokens, maximum, number, parameter, text)
  - llama3.2:3b: conflict (conf 0.80, score 0.64, grounded: analyze_frequency, encode, encoding, frequencies, max_tokens, parameter, returns)
- **pair_12_pallets_click_t2068_f2v4** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.75).
  - gemma3:4b: conflict (conf 0.95, score 0.75, grounded: arguments, click, commands, compatibility, construction, functionality, handling, original, parameter, quote, shell, shlex, test_edit_error_handling_with_editor_args, test_edit_file_with_editor_args, test_edit_with_no_editor_args, test_edit_with_non_shell_safe_editor_args)
  - deepseek-coder:6.7b: conflict (conf 0.50, score 0.54, grounded: click, editor_args, list, parameter, properly, str)
  - llama3.2:3b: conflict (conf 0.80, score 0.57, grounded: carefully, constructed, editing, editor_args, env, list, non, require_save, safe, shell)
- **pair_13_pallets_click_t2956_f3v8** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.80).
  - gemma3:4b: conflict (conf 1.00, score 0.74, grounded: across, click, default, multiply_by_two, runner, test_option_history_callback_modifications, test_option_history_multiple_executions, tracking, values)
  - deepseek-coder:6.7b: conflict (conf 1.00, score 0.80, grounded: command, processing, runner, test_option_history_callback_modifications, test_option_history_integration_with_groups, test_option_history_multiple_executions, tracking)
  - llama3.2:3b: conflict (conf 0.80, score 0.79, grounded: default, enables, history, independent, its, missing, option, overrides, own, test_option_history_callback_modifications, test_option_history_integration_with_groups, test_option_history_multiple_executions, tracking, values)
- **pair_14_pallets_jinja_t1621_f1v6** (truth: conflict) — A=escalate, B=conflict, C=no_conflict via `weighted_evidence_vote`
  - Rationale quality is comparable (margin 0.03 < 0.12); confidence-weighted evidence favors 'no_conflict' (conflict=0.49 vs no_conflict=0.59, gap 0.09).
  - gemma3:4b: no_conflict (conf 1.00, score 0.59, grounded: across, aliasing, dictloader, empty, filesystemloader, functionality, functionloader, loader, loaders, normalization, path_transform, template, testpathtransformation)
  - deepseek-coder:6.7b: conflict (conf 0.50, score 0.57, grounded: correctly, html, mobile, prefix, removal, tpl, transformation, work)
  - llama3.2:3b: conflict (conf 0.80, score 0.62, grounded: lookup, mapping, path, transformation, transformed)
- **pair_15_pallets_jinja_t1559_f2v7** (truth: no_conflict) — A=escalate, B=conflict, C=escalate via `ambiguous_evidence`
  - Contradictory verdicts with rationale scores within 0.12 (margin 0.00) and weighted evidence within 0.05 (gap 0.04); genuine ambiguity, escalating.
  - gemma3:4b: no_conflict (conf 1.00, score 0.77, grounded: available, callables, fallback, fallback1_gettext, fallback2_gettext, i18n, items, jinja2, ngettext, original, primary, primary_gettext, translations)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.77, grounded: fallback, fallbacks, functionality, gettext, i18n, languages, multiple, ngettext, order, tags, trans)
  - llama3.2:3b: conflict (conf 0.80, score 0.71, grounded: fallback, french, german, hello, hola, primary, spanish, test_multiple_fallbacks, translations)
- **pair_16_pillow_t290_f1v5** (truth: conflict) — A=conflict, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.66).
  - gemma3:4b: conflict (conf 0.95, score 0.65, grounded: _adjust_palette_lightness, adjustment, brightness, colors, lightness_factor, palette, pil, quantization, quantize, used)
  - deepseek-coder:6.7b: conflict (conf 1.00, score 0.66, grounded: colors, dither, image, kmeans, lightness, lightness_factor, palette, pil, properly, quantization, quantize)
  - llama3.2:3b: conflict (conf 0.80, score 0.60, grounded: adjust, adjustment, brightness, colors, image, lightness_factor, palette, quantization, quantize)
- **pair_17_pillow_t25_f1v5** (truth: no_conflict) — A=escalate, B=conflict, C=escalate via `ambiguous_evidence`
  - Contradictory verdicts with rationale scores within 0.12 (margin 0.08) and weighted evidence within 0.05 (gap 0.03); genuine ambiguity, escalating.
  - gemma3:4b: conflict (conf 0.95, score 0.49, grounded: _ensure_mutable, check, corner, filename, image, images, mark_corners, marked, original, parameter, pixel, save)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.49, grounded: corner, filename, image, pixel, readonly, save, saved)
  - llama3.2:3b: conflict (conf 0.80, score 0.57, grounded: check, color, corners, filename, mark_corners, marking, parameter, readonly, red, save)
- **pair_19_samuelcolvin_dirty_equals_t43_f1v3** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.71).
  - gemma3:4b: conflict (conf 0.75, score 0.55, grounded: address, checks, domain, isemail, matching, sensitivity)
  - deepseek-coder:6.7b: conflict (conf 0.50, score 0.71, grounded: isip, netmask, requires, specified, test_ip_bad_netmask, typeerror, version)
  - llama3.2:3b: conflict (conf 0.80, score 0.62, grounded: basic, checking, checks, format, isemail, specified)

## Structured representation

| Policy | Coverage | Escalations | Accuracy | Precision | Recall | F1 | Avg rationale | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A_current_escalation | 0.0% | 16/16 (100.0%) | 0.0% | 0.0% | 0.0% | 0.0% | n/a | n/a |
| B_majority_vote | 100.0% | 0/16 (0.0%) | 56.2% | 56.2% | 100.0% | 72.0% | n/a | n/a |
| C_evidence_weighted | 93.8% | 1/16 (6.2%) | 56.2% | 60.0% | 100.0% | 75.0% | 0.636 | 7.54ms |

### Per-pair decisions (policy C)

- **pair_01_dottxt_ai_outlines_t1655_f9v10** (truth: conflict) — A=escalate, B=conflict, C=conflict via `rationale_dominance`
  - llama3.2:3b gave the strongest grounded rationale (score 0.66 vs 0.00, margin 0.66 >= 0.12); verdict 'conflict' accepted over deepseek-coder:6.7b despite the vote split. Grounded evidence: ['braces', 'curly', 'format', 'guid', 'hash_sha256', 'style', 'windows'].
  - gemma3:4b: conflict (conf 0.95, score 0.61, grounded: guid, hash, hash_sha256, sha, windows)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.00, grounded: none)
  - llama3.2:3b: conflict (conf 0.80, score 0.66, grounded: braces, curly, format, guid, hash_sha256, style, windows)
- **pair_02_dottxt_ai_outlines_t1655_f3v9** (truth: no_conflict) — A=escalate, B=conflict, C=escalate via `ambiguous_evidence`
  - Contradictory verdicts with rationale scores within 0.12 (margin 0.11) and weighted evidence within 0.05 (gap 0.02); genuine ambiguity, escalating.
  - gemma3:4b: conflict (conf 0.95, score 0.53, grounded: braces, number, octal_str, prefix, style, windows)
  - deepseek-coder:6.7b: no_conflict (conf 1.00, score 0.54, grounded: guid, octal_str)
  - llama3.2:3b: conflict (conf 0.80, score 0.65, grounded: character, characters, guid, octal_str, segment, whitespace)
- **pair_03_dspy_t8587_f3v5** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.65).
  - gemma3:4b: conflict (conf 0.85, score 0.65, grounded: _safe_truncate, allow_reuse, cache_hit, custom, debug, dspy, including, logger, logging, messages, might, receive, setup, streaming)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.52, grounded: provided, receive)
  - llama3.2:3b: conflict (conf 0.80, score 0.63, grounded: _buffered_message_end_with_start_identifier, provided, receive)
- **pair_04_dspy_t8563_f1v2** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.84).
  - gemma3:4b: conflict (conf 0.95, score 0.84, grounded: _parse_literal_value, adapters, append, ast, attribute, basemodel, body, constant, convert_input_schema_to_tool_args, create_model, dict, dspy, elts, expr, func_name, input_str, isinstance, keywords, list, match, model_validate, model_validator, node, operand, parsed, parsed_value, parsing, pydantic, strip, syntaxerror, test_parse_python_calls_basic, test_parse_python_calls_multiple, test_parse_python_calls_positional_error, test_parse_python_calls_variable_error, test_toolcalls_validate_input_with_multiple_calls, test_toolcalls_validate_input_with_string, text, tree, tuple, typeadapter, uadd, unaryop, usub, validate_input_before, zip)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.70, grounded: args, input_str, parse_python_calls, provided, signature)
  - llama3.2:3b: conflict (conf 0.80, score 0.67, grounded: provided, validate_input, validate_input_before)
- **pair_07_huggingface_datasets_t6252_f3v5** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.68).
  - gemma3:4b: conflict (conf 0.95, score 0.67, grounded: asarray, astype, decode_example, dict, float32, image_array, ndarray, pil, test_image_decode_as_array, token_per_repo_id, union, value)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.68, grounded: decode_example, image, ndarray, pil, union)
  - llama3.2:3b: conflict (conf 0.80, score 0.37, grounded: as_array, image)
- **pair_08_huggingface_datasets_t6252_f1v3** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.65).
  - gemma3:4b: conflict (conf 0.95, score 0.64, grounded: abs, aspect, decode_example, decoded, image, lanczos, max_resolution, max_size, new_aspect_ratio, original_aspect_ratio, original_image, preserved, resampling, test_image_decode_with_max_resolution, thumbnail)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.63, grounded: decode_example, image, pil, token_per_repo_id, value)
  - llama3.2:3b: conflict (conf 0.80, score 0.65, grounded: decode_example, parameter, shared_datadir, test_image_decode_with_max_resolution, token_per_repo_id, value)
- **pair_09_llama_index_t18813_f1v3** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.88).
  - gemma3:4b: conflict (conf 0.85, score 0.75, grounded: as_base64, base, bool, bytesio, core, llama_index, llms, resolve_audio_with_size, test_document_block_resolve_document_with_size, test_image_block_resolve_image_with_size, tuple)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.79, grounded: base, core, int, llama_index, llms, resolve_document, resolve_image_with_size, seek, tell)
  - llama3.2:3b: conflict (conf 0.80, score 0.88, grounded: base, core, llama_index, llms, resolve_audio_with_size, resolve_document_with_size, seek, tell, test_audio_block_resolve_audio_with_size)
- **pair_10_llama_index_t17244_f3v4** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.77).
  - gemma3:4b: conflict (conf 0.85, score 0.77, grounded: as_base64, b64decode, b64encode, bool, bytesio, getvalue, image_to_base64, imageblock, len, read_bytes, resolve_image, resolved, startswith, str, test_image_block_force_mimetype, valueerror)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.43, grounded: as_base64, bool, bytesio, force_mimetype, str)
  - llama3.2:3b: conflict (conf 0.80, score 0.70, grounded: as_base64, bool, bytesio, force_mimetype, normalize_image_bytes, resolve_image, str, tuple)
- **pair_11_openai_tiktoken_t0_f1v3** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.75).
  - gemma3:4b: conflict (conf 0.85, score 0.75, grounded: _count_token_frequency, analyze_frequency, basic, bool, dictionary, encode, encoding, frequencies, list, max_tokens, means, simple, test_token_limit, testing, tiktoken, tokens, tuple, union)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.66, grounded: _core_bpe, _count_token_frequency, _special_token_regex, analyze_frequency, bool, decode, dict, frequencies, frozenset, group, int, isinstance, list, match, parameter, raise_disallowed_special_token, search, special_tokens_set, text, tuple, union)
  - llama3.2:3b: conflict (conf 0.80, score 0.38, grounded: encode)
- **pair_12_pallets_click_t2068_f2v4** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.57).
  - gemma3:4b: conflict (conf 0.85, score 0.57, grounded: carefully, cmd_parts, edit_file, editor_args, extend, list, modified, original, properly, shlex, str, use)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.56, grounded: editor_args, env, extension, filename, list, require_save, text, txt)
  - llama3.2:3b: conflict (conf 0.80, score 0.56, grounded: click, cmd_parts, edit_file)
- **pair_13_pallets_click_t2956_f3v8** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.85).
  - gemma3:4b: conflict (conf 0.75, score 0.77, grounded: click, correctly, doesn, get_option_history, test_option_history_callback_modifications, test_option_history_command_line_override, test_option_history_edge_case_empty_value, test_option_history_integration_with_groups, test_option_history_multiple_executions, test_option_history_multiple_options, test_option_history_nonexistent_option, test_option_history_tracking_basic, test_option_history_tracking_disabled, track_changes, tracked, tracking, verbose_history)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.45, grounded: multiply_by_two, provided)
  - llama3.2:3b: conflict (conf 0.80, score 0.85, grounded: assert_info_dict_superset, check_superset, provided, test_parameter)
- **pair_14_pallets_jinja_t1621_f1v6** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.81).
  - gemma3:4b: conflict (conf 0.95, score 0.81, grounded: bad_transform, based, complex_transform, create, dictloader, endswith, environment, functionality, get_template, includes, loaders, original, paths, raise, render, replace, selection, simulate, startswith, template, templates, test_path_transform_with_complex_logic, test_path_transform_with_invalid_input, valueerror, version)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.30, grounded: test_path_transform_with_invalid_input)
  - llama3.2:3b: conflict (conf 0.80, score 0.72, grounded: bad_transform, complex_transform, test_path_transform_with_complex_logic, test_path_transform_with_invalid_input)
- **pair_15_pallets_jinja_t1559_f2v7** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.80).
  - gemma3:4b: conflict (conf 0.95, score 0.80, grounded: _make_new_ngettext_with_fallback, env, environment, extensions, fallback1_gettext, fallback2_gettext, fallback_funcs, fallback_ngettext, fallback_ngettext_funcs, fallback_rv, fallbacks, from_string, install_gettext_callables_with_fallback, jinja2, multiple, primary_gettext, primary_ngettext, render, test_ngettext_fallback_basic, translations, variable)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.71, grounded: fallback2_gettext, primary_gettext, provided, test_multiple_fallbacks)
  - llama3.2:3b: conflict (conf 0.80, score 0.60, grounded: _install_callables_with_fallback, fallback_gettext_funcs, provided)
- **pair_16_pillow_t290_f1v5** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.69).
  - gemma3:4b: conflict (conf 0.85, score 0.54, grounded: _adjust_palette_lightness, colors, dither, its, kmeans, lightness_factor, palette, pil, quantization, values)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.66, grounded: colors, dither, kmeans, lightness_factor, palette, quantize)
  - llama3.2:3b: conflict (conf 0.80, score 0.69, grounded: _adjust_palette_lightness, _new, convert, quantize)
- **pair_17_pillow_t25_f1v5** (truth: no_conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.71).
  - gemma3:4b: conflict (conf 0.85, score 0.71, grounded: images, mark_corners, marking, original, putpixel, red_color, save, test_mark_corners, test_no_corner_marking)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.52, grounded: format, params, save)
  - llama3.2:3b: conflict (conf 0.80, score 0.59, grounded: path, save, test_mark_corners)
- **pair_19_samuelcolvin_dirty_equals_t43_f1v3** (truth: conflict) — A=escalate, B=conflict, C=conflict via `unanimous`
  - All 3 models agree on 'conflict' (best rationale score 0.86).
  - gemma3:4b: conflict (conf 0.95, score 0.78, grounded: com, dirty_equals, functioncheck, info, isemail, isjson, isuuid, long_email, mark, org, parametrize, pytest, tag, test_is_email_domain_filtering, test_is_email_domain_repr, test_is_email_edge_cases, test_is_email_false, test_is_email_repr, test_is_email_true, user123, user_name)
  - deepseek-coder:6.7b: conflict (conf 0.95, score 0.86, grounded: dirty, functioncheck, isemail, isjson, isuuid, test_is_email_domain_filtering, test_is_email_domain_repr, test_is_email_edge_cases, test_is_email_false, test_is_email_repr, test_is_email_true)
  - llama3.2:3b: conflict (conf 0.80, score 0.69, grounded: dirty_equals, dirtyequals, isemail, str, test_is_email_repr)

## Success criteria

- raw: coverage 87.5% (PASS >70%), escalation 12.5% (PASS <25%), F1 76.2% vs current 100.0% (PASS)
- structured: coverage 93.8% (PASS >70%), escalation 6.2% (PASS <25%), F1 75.0% vs current 0.0% (PASS)

Note: the current policy's F1 is computed only over the pairs it decided (its coverage is near zero), so it is not directly comparable; the F1 check passes when evidence-weighted adjudication maintains F1 at dramatically higher coverage.
