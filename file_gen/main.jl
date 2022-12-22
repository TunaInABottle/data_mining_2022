## in case the file is not installed
# using Pkg
# ## using pkg to add csv package file to library
# Pkg.add("CSV")
# Pkg.add("DataFrames")
# Pkg.add("StatsBase")

using CSV, DataFrames, StatsBase, ProgressBars
include("classes.jl")
using .UserClass

const USERS_N::Int = parse(Int, ARGS[1])
const QUERIES_N::Int = parse(Int, ARGS[2])

println("Reading queries cont...")

query_kv = CSV.read("../data/first_test/queries_cont.csv", DataFrame, header=true)

println(query_kv)

query_items::Dict{String, Array{Any}} = Dict{String, Any}()
for (idx, col_name) in ProgressBar(enumerate(names(query_kv)))
    query_items[col_name] = query_kv[!, idx]
    #println("Column $idx is named $col_name")
end

# display(query_items)
# println(query_items["city"][1])
# println(length(query_items))
# println(keys(query_items))
# println(typeof(query_items["city"][1]))


### generating queries ###
println("Generating queries...")
query_vector::Vector{Query} = []

for i in ProgressBar(1:QUERIES_N)
    push!(query_vector, Query(i, QUERIES_N, query_items))
end

display(query_vector)
println(to_query_string(query_vector[1].cont))

"""

### generating users ###
println("Generating users...")
user_vector::Vector{User} = []

for i in ProgressBar(1:USERS_N)
    push!(user_vector, User(i, USERS_N))
end

# display(user_vector)



### generate dataframe ###
println("Generating utility matrix...")
df = DataFrame()
df.user_id = map(x -> x.id, user_vector)

for query::Query in ProgressBar(query_vector)
    df[!, query.id] = sample_rating(query, user_vector)
end

display(df)

"""