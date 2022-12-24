## in case the file is not installed
# using Pkg
# ## using pkg to add csv package file to library
# Pkg.add("CSV")
# Pkg.add("DataFrames")
# Pkg.add("StatsBase")
# Pkg.add("ProgressBars")

using CSV, DataFrames, StatsBase, ProgressBars, ArgParse
include("classes.jl")
using .UserClass

using ArgParse

function parse_commandline()
    s = ArgParseSettings()
    @add_arg_table! s begin
        "--folder", "-f"
            help = "Where to save the generated files"
            arg_type = String
            default = "tmp"
            #action = :store_true
            #required = true
        "arg1"
            help = "number of users to be generated"
            arg_type = Int
        "arg2"
            help = "number of queries to be generated"
            arg_type = Int

    end
    return parse_args(s)
end

parsed_args = parse_commandline()

const USERS_N::Int = parsed_args["arg1"]
const QUERIES_N::Int = parsed_args["arg2"]
const FOLDER_NAME::String = parsed_args["folder"]

if !isdir("../data/$(FOLDER_NAME)")
    mkdir("../data/$(FOLDER_NAME)")
end

println("Reading queries cont...")

query_kv = CSV.read("queries_content.csv", DataFrame, header=true)
# writing it in the new folder
CSV.write("../data/$(FOLDER_NAME)/query_content.csv", query_kv)

query_items::Dict{String, Array{Any}} = Dict{String, Any}()
for (idx, col_name) in ProgressBar(enumerate(names(query_kv)))
    query_items[col_name] = query_kv[!, idx]
    #println("Column $idx is named $col_name")
end

### generating queries ###
println("Generating queries...")
query_vector::Vector{Query} = []

for i in ProgressBar(1:QUERIES_N)
    push!(query_vector, Query(i, QUERIES_N, query_items))
end

#display(query_vector)
#println(to_query_string(query_vector[1].cont))

query_df = DataFrame()
query_df[!, "id"] = map(x -> x.id, query_vector)
query_df[!, "content"] = map(x -> to_query_string(x.cont), query_vector)

#display(query_df)
println("Saving query dataset...")
CSV.write("../data/$(FOLDER_NAME)/queries.csv", query_df)


### generating users ###
println("Generating users...")
user_vector::Vector{User} = []

for i in ProgressBar(1:USERS_N)
    push!(user_vector, User(i, USERS_N))
end

user_df = DataFrame()
user_df[!, "id"] = map(x -> x.id, user_vector)

println("Saving user dataset...")
CSV.write("../data/$(FOLDER_NAME)/users.csv", user_df)


### generate utility matrix ###
println("Generating utility matrix...")
utility_matrix = DataFrame()
utility_matrix.user_id = map(x -> x.id, user_vector)

for query::Query in ProgressBar(query_vector)
    utility_matrix[!, query.id] = sample_rating(query, user_vector)
end

println("Saving utility matrix...")
CSV.write("../data/$(FOLDER_NAME)/utility_matrix.csv", utility_matrix)
println("Done!")