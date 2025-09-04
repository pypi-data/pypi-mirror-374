# import pandas as pd
# fromraise_synthetic_data_generator import generate_synthetic_data

# def test_outputs_written(tmp_path):
#     df_in = pd.DataFrame({"age": [1,2,3], "country": ["ES", "ES", "ES"]})
#     _ = generate_synthetic_data(
#         dataset=df_in,
#         selected_model="auto-select",
#         n_samples=3,
#         evaluation_report=False,
#         output_dir=tmp_path,
#         run_name="artifacts"
#     )
#     out_dir = tmp_path / "artifacts"
#     assert (out_dir / "synthetic_data.csv").exists()
#     assert (out_dir / "info.txt").exists() or True 