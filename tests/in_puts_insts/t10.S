fld  f2, 100(x1)
fadd f4, f2, f3
fmul f6, f4, f2
fdiv f8, f6, f4
fsub f10, f8, f2
fadd f12, f10, f6
fmul f14, f12, f8
fdiv f16, f14, f10
fadd f18, f16, f12
fsd  f18, 200(x2)