for (u64 i=0; i<count; i++, T+=G) {
    u64 V; fread(&V,8,1,g);
    u64 u = T ^ S, W = fmix(u) ^ V;
    u32 pos = W & 0xffffff, c = (W>>24) & 0xffffff;
    if ((fmix(((u64)c<<24 | pos) ^ u) >> 48) != (W>>48)) die("MAC");
    u32 r = find(pos), a = col[r];
    S = upd(S, T, sz[r], Hh[r], a, c); // preenchimento real
    if (a != c) { // recolore e funde
        lrem(r); col[r] = c;
        cand = componentes_com_cor(c) \ {r}; // lista por cor
        ladd(r);
        for (x : cand) if (adjacent(find(r), x)) unite(find(r), x);
        r = find(r);
    }
    for (j=0; j<decoys; j++) { // decoys: mesmas (n,H)
        u64 x = T ^ S ^ (j+1)*D, rc = (fmix(x) & 0xfffffe) | 1;
        while (rc == 0xf2eadf) { x = fmix(x+G); rc = (fmix(x) & 0xfffffe) |
1; }
        S = upd(S,T, sz[r],Hh[r], c, rc);
        S = upd(S,T, sz[r],Hh[r], rc, c);
    }
}