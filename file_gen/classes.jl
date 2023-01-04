
module UserClass
    using Printf, StatsBase
    export User, Query, sample_rating, to_query_string

    const TRENDS_WEIGTHS = Weights([10, 10, 60, 20, 5]) # rated: highly, lowly, average, divisive, randomly

    const QUERY_LENGTH_INTERVAL = 1:3
    const QUERY_LENGTH_WEIGTHS = Weights([15, 75, 10])
    const LEGTHEN_QUERY_CHANCE::Float64 = 0.3 # after deciding the base length, which is the probability to make it even longer

    function id_pad(name::String, n::Int, max::Int)::String
        return "$(name)_$(lpad(n, length(string(max)), '0'))"
    end

    #################
    ##### users #####
    #################

    # id : integer that identify the User
    struct User
        id::String
        rating_interval::UnitRange{Int}
        # max : maximum number of users, used for padding
        User(id::Int, max::Int) = new(id_pad("user", id, max), 1:100)
    end
    Base.show(io::IO, ::MIME"text/plain", user::User) = @printf(io, "User %s interval %s", user.id, user.rating_interval)


    ########################
    ##### query trends #####
    ########################



    @enum TREND begin
        #null_trend = 0
        T_highly_rated = 1
        T_lowly_rated
        T_average_rated
        T_divisive_rated
        T_randomly_rated
    end
    const QUERY_TREND_VALS = Set(Int(val) for val in instances(TREND))
    
    function sample_trend()::TREND
        return TREND(sample(collect(QUERY_TREND_VALS), TRENDS_WEIGTHS))
    end


    ###################
    ##### queries #####
    ###################
 
    
    struct Query
        id::String
        trend::TREND
        density::Float64
        rating_interval::UnitRange{Int}
        cont::Dict{String, Any}

        function Query(id::Int, max::Int, cont_set::Dict{String, Array{Any}})
            trend::TREND = sample_trend()
            density::Float64 = random_trend_density(trend)
            rating_interval::UnitRange{Int} = random_rating_interval(trend)
            cont::Dict{String, Any} = random_query_cont(cont_set)
            new(id_pad("query", id, max), trend, density, rating_interval, cont)
        end
    end
    Base.show(io::IO, ::MIME"text/plain", query::Query) = @printf(io, "Query %s, trend %s, density %s, rating_interval %s, query %s", query.id, query.trend, query.density, query.rating_interval, query.cont)
    

    function random_query_cont(cont_set::Dict{String, Array{Any}})::Dict{String, Any}
        keys_n = sample(QUERY_LENGTH_INTERVAL, QUERY_LENGTH_WEIGTHS)
        keys_vect = collect(keys(cont_set))
        query_sampled_keys::Vector{String} = sample(keys_vect, keys_n, replace=false)

        # add further queries (so to models queries longer than the baseline)
        stop_flag::Bool = false
        while !stop_flag && length(query_sampled_keys) < length(keys_vect)
            if rand() < LEGTHEN_QUERY_CHANCE
                left_keys = setdiff(keys_vect, query_sampled_keys)
                push!(query_sampled_keys, sample(left_keys, 1, replace=false)[1])
            else
                stop_flag = true
            end
        end

        # println("query_sampled_keys: $query_sampled_keys")
        query_cont = Dict{String, Any}()
        for key in query_sampled_keys
            query_cont[key] = sample(cont_set[key], 1, replace=false)[1]
        end

        #println("resulting query: $query_cont\n\n")
        return query_cont
    end

    function random_trend_density(trend::TREND)::Float64
        # Tried to use switch, but it does not work
        # @match this_trend begin
        #     Int(T_highly_rated::TREND) => println("it exists")
        #     Int(T_lowly_rated::TREND)  => println("it exists, somehow")
        #     _              => println("it does not exist")
        # end
        if trend == T_highly_rated::TREND
            return sample(1:00.1:80)/100
        elseif trend == T_lowly_rated::TREND
            return sample(1:00.1:60)/100
        elseif trend == T_average_rated::TREND || trend == T_divisive_rated::TREND
            return sample(5:00.1:75)/100
        elseif trend == T_randomly_rated::TREND
            return sample(1:00.1:50)/100
        else
            throw("Trend $trend unexpected")
        end
    end

    function random_rating_interval(trend::TREND)::UnitRange{Int}
        min_noise::Int = sample(0:20)
        max_noise::Int = sample(0:20)

        if trend == T_highly_rated::TREND
            return (75 - Int(round(min_noise / 2))):(80 + max_noise)
        elseif trend == T_lowly_rated::TREND
            return (min_noise):(50 + max_noise)
        elseif trend == T_average_rated::TREND
            return (44 - min_noise):(65 + max_noise)
        elseif trend == T_divisive_rated::TREND
            return min_noise:(80 + max_noise)
        elseif trend == T_randomly_rated::TREND
            return min_noise:(80 + max_noise)
        else
            throw("Trend $trend unexpected")
        end
    end

    function sample_rating(query::Query, users::Vector{User})::Vector{Union{Missing,Int}}
        ratings = Vector{Union{Missing, Int}}(missing, length(users))

        scores = Vector{Int}()
        users_idx = Vector{Int}()

        try 
            # sample scores
            scores = sample(query.rating_interval, Int(round(query.density * length(users))))
            #sample users
            users_idx = sample(1:length(users), Int(round(query.density * length(users))), replace=false)
        catch e
            println("Error sampling query $query")
            println("Items to be sampled $(Int(round(query.density * length(users))))")
            println("length(users): $(length(users))")
            println("scores: $(scores)")
            throw(e)
        end

        # assign scores to users
        for (idx, user) in enumerate(users_idx)
            ratings[user] = scores[idx]
        end
        return ratings
    end


    function to_query_string(query_dict::Dict{String, Any})::String
        query_string = []
        for (key, val) in query_dict
            push!(query_string, "$key=$(string(val))")
        end
        return join(query_string, " AND ")
    end
end