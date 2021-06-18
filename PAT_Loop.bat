FOR /L %%I IN (5,10,506) DO start /WAIT PAT3/PAT3.Console.exe temp/csp_out/%%I.csp ../profiles/csp/%%I
pause