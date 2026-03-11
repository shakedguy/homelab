namespace tests.Utils;

using System;
using System.Numerics;

public readonly struct RangeSeed<T>(T start, T end)
    where T : INumber<T>
{
    public T Start { get; } = start;
    public T End { get; } = end;

    public RangeWithStep<T> GetEnumerator()
    {
        var dir = End >= Start ? T.One : -T.One;
        return new RangeWithStep<T>(Start, End, dir);
    }

    public static RangeWithStep<T> operator >> (RangeSeed<T> seed, T step)
    {
        if (step == T.Zero)
            throw new ArgumentException("Step cannot be zero.", nameof(step));

        var dir = seed.End >= seed.Start ? T.One : -T.One;
        var mag = T.Abs(step);
        var signed = mag * dir;
        return new RangeWithStep<T>(seed.Start, seed.End, signed);
    }
}

public readonly struct RangeWithStep<T> where T : INumber<T>
{
    public T Start { get; }
    public T End { get; }
    public T Step { get; }

    public RangeWithStep(T start, T end, T step)
    {
        if (step == T.Zero)
            throw new ArgumentException("Step cannot be zero.", nameof(step));

        Start = start;
        End = end;
        Step = step;
    }

    public static implicit operator Range(RangeWithStep<T> range)
        => new(new Index(int.CreateChecked(range.Start)), int.CreateChecked(range.End));

    public RangeEnumerator<T> GetEnumerator() => new(Start, End, Step);
}

public struct RangeEnumerator<T>(T start, T end, T step)
    where T : INumber<T>
{
    private readonly bool _ascending = step > T.Zero;
    private bool _started = false;


    public T Current { get; private set; } = start;

    public bool MoveNext()
    {
        if (!_started)
        {
            _started = true;
            return true;
        }

        var next = Current + step;

        if (_ascending)
        {
            if (next >= end) return false;
            Current = next;
            return true;
        }

        if (next <= end) return false;
        Current = next;
        return true;
    }
}

public static class RangeGenericExtensions
{
    public static RangeEnumerator<T> GetEnumerator<T>(this (T start, T end, T step) tuple)
        where T : INumber<T>
        => new(tuple.start, tuple.end, tuple.step);
}