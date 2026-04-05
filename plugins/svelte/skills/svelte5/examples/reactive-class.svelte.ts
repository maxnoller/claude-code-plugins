// Reactive class with $state fields
// File: todo.svelte.ts

// Class instances can have $state fields for reactivity
export class Todo {
    // $state fields become reactive properties
    done = $state(false);

    // Can also assign $state in constructor
    text: string;
    createdAt: Date;

    constructor(text: string) {
        // First assignment inside constructor body is tracked
        this.text = $state(text);
        this.createdAt = $state(new Date());
    }

    // Use arrow function to preserve `this` binding
    toggle = () => {
        this.done = !this.done;
    };
}

// Factory function pattern with runes in .svelte.ts files
export function createTodoList(initial: string[] = []) {
    let todos = $state<Todo[]>(initial.map(text => new Todo(text)));

    // Expose getters for derived values
    return {
        get todos() { return todos },
        get completed() { return todos.filter(t => t.done) },
        get pending() { return todos.filter(t => !t.done) },
        get count() { return todos.length },

        add(text: string) {
            todos.push(new Todo(text));
        },

        remove(todo: Todo) {
            const index = todos.indexOf(todo);
            if (index !== -1) {
                todos.splice(index, 1);
            }
        },

        clearCompleted() {
            // Filter out completed and reassign to trigger reactivity
            todos = todos.filter(t => !t.done);
        }
    };
}
