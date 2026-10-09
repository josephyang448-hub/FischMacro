BUILD A WINDOWS EXE WITHOUT INSTALLING PYTHON ON YOUR PC

This project includes a GitHub Actions workflow that builds the EXE on a hosted Windows runner.

1. Sign in to GitHub and create a new repository. A free account is sufficient.
2. Upload the contents of this folder to the repository (including the hidden .github/workflows/build-windows.yml file).
3. Open the repository's Actions tab and select "Build Windows EXE".
4. If the workflow has not started automatically, click "Run workflow".
5. Wait for the run to finish successfully.
6. Open the completed workflow run and download the artifact named "FischSwiftStyle-Windows-EXE".
7. Extract the downloaded artifact ZIP; it contains FischSwiftStyle.exe.

The build runner installs Python and packages only on the hosted build machine. Your PC does not need Python to run the resulting EXE.

NOTE: This is still the V1 visual-detection prototype. It does not implement automated fishing actions or Roblox memory reading. Review the source before running any executable.
