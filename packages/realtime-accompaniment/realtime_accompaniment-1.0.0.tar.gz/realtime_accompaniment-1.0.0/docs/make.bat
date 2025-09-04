@REM Makefile for Sphinx documentation
@REM

@REM You can set these variables from the command line.
SET SPHINXOPTS=
SET SPHINXBUILD=sphinx-build
SET SOURCEDIR=.
SET BUILDDIR=_build

@REM Internal variables.
SET ALLSPHINXOPTS=-d %BUILDDIR%/.doctrees %SPHINXOPTS% %SOURCEDIR%
SET BUILDDIR_ABSPATH=%CD%\%BUILDDIR%

@REM the i18n builder cannot share the environment and depends on the
@REM location, so in case we were built in a different directory, we
@REM need to repoint to the source directory
IF NOT EXIST %SOURCEDIR%\ %SPHINXBUILD%\%SPHINXBUILD%.exe (
	SET SOURCEDIR=.
)

@REM Put it first so that "make" without argument is like "make help".
help:
	%SPHINXBUILD% -M help %ALLSPHINXOPTS% %O%

.PHONY: help Makefile

@REM Catch-all target: route all unknown targets to Sphinx using the new
@REM "make mode" option.  %O% is meant as a shortcut for %SPHINXOPTS%.
%: Makefile
	%SPHINXBUILD% -M %* %ALLSPHINXOPTS% %O%
