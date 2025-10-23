
str = """
B 2x1 A
TT, Kas, Mig

B 0 x 2 V
Lucca, lucca

V 0 x 0 A

A 1 x 0 B
Guto

A 1 x 2 V
TT, Liba, Liba

V 2 x 0 B
Marcelo, Pig

V 0 x 2 A
Tulio, Yuri

A 0 x 0 B

B 0 x 0 V

V 2 x 0 A
Liba, Liba

V 2 x 0 B
Lucca, Pig

V 1 x 1 A
Tulio, lucca

A 0 x 0 B
"""

linhas = split(str, "\n\n")

dict_art = Dict{String, Int}()
dict_plac = Dict{Tuple{Char, Char}, Tuple{Int, Int, Int}}()

for linha in linhas
    spl = split(strip(linha), "\n")
    @assert 0 < length(spl) < 3
    placar = spl[1]

    lado1, lado2 = split(uppercase(placar), "X")
    time1, time2 = lado1[1], lado2[end]
    gols1, gols2 = strip(lado1[2:end]), strip(lado2[1:end-1])

    # time1, gols1, gols2, time2 = match(r"([VAB]) (\d+) x (\d+) ([VAB])", placar).captures
    gols = length(spl) > 1 ? split(spl[2], " ") : String[]

    if [time1, time2] == ['A', 'B']
        golsA = get(dict_plac, ('A','B'), (0,0,0))[1] + parse(Int, gols1)
        golsB = get(dict_plac, ('A','B'), (0,0,0))[2] + parse(Int, gols2)
        n = get(dict_plac, ('A','B'), (0,0,0))[3] + 1
        dict_plac[('A','B')] = (golsA, golsB, n)
    elseif [time1, time2] == ['B', 'A']
        golsB = get(dict_plac, ('A','B'), (0,0,0))[2] + parse(Int, gols1)
        golsA = get(dict_plac, ('A','B'), (0,0,0))[1] + parse(Int, gols2)
        n = get(dict_plac, ('A','B'), (0,0,0))[3] + 1
        dict_plac[('A','B')] = (golsA, golsB, n)
    elseif [time1, time2] == ['V', 'A']
        golsV = get(dict_plac, ('V','A'), (0,0,0))[1] + parse(Int, gols1)
        golsA = get(dict_plac, ('V','A'), (0,0,0))[2] + parse(Int, gols2)
        n = get(dict_plac, ('V','A'), (0,0,0))[3] + 1
        dict_plac[('V','A')] = (golsV, golsA, n)
    elseif [time1, time2] == ['A', 'V']
        golsA = get(dict_plac, ('V','A'), (0,0,0))[2] + parse(Int, gols1)
        golsV = get(dict_plac, ('V','A'), (0,0,0))[1] + parse(Int, gols2)
        n = get(dict_plac, ('V','A'), (0,0,0))[3] + 1
        dict_plac[('V','A')] = (golsV, golsA, n)
    elseif [time1, time2] == ['B', 'V']
        golsB = get(dict_plac, ('B','V'), (0,0,0))[1] + parse(Int, gols1)
        golsV = get(dict_plac, ('B','V'), (0,0,0))[2] + parse(Int, gols2)
        n = get(dict_plac, ('B','V'), (0,0,0))[3] + 1
        dict_plac[('B','V')] = (golsB, golsV, n)
    elseif [time1, time2] == ['V', 'B']
        golsV = get(dict_plac, ('B','V'), (0,0,0))[2] + parse(Int, gols1)
        golsB = get(dict_plac, ('B','V'), (0,0,0))[1] + parse(Int, gols2)
        n = get(dict_plac, ('B','V'), (0,0,0))[3] + 1
        dict_plac[('B','V')] = (golsB, golsV, n)
    else
        @error("Times inválidos\n$linha")
    end

    for gol in gols
        stripped = strip(strip(gol), ',')
        @show linha
        @show stripped
        nome = uppercase(stripped[1]) * lowercase(stripped[2:end])
        dict_art[nome] = get(dict_art, nome, 0) + 1
    end
end

println("V $(dict_plac[('V','A')][1]) x $(dict_plac[('V','A')][2]) A - $(dict_plac[('V','A')][3]) jogos")
println("A $(dict_plac[('A','B')][1]) x $(dict_plac[('A','B')][2]) B - $(dict_plac[('A','B')][3]) jogos")
println("B $(dict_plac[('B','V')][1]) x $(dict_plac[('B','V')][2]) V - $(dict_plac[('B','V')][3]) jogos")

println("\nTotal de gols: $(sum(el[1] + el[2] for el in values(dict_plac)))\n")

sorted_players = sort(collect(keys(dict_art)))
for jogador in sorted_players
    println("$(jogador): $(dict_art[jogador])")
end

println("\nTotal de gols por jogadores: $(sum(values(dict_art)))")
